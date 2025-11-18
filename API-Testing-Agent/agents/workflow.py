"""
Simple Workflow - No LangGraph needed!

This is a simple step-by-step workflow that:
1. Runs Document Classifier Agent → Gets document classifications
2. Runs API Testing Agent → Tests APIs with those documents
3. Generates a report

Think of it like: A checklist that runs each step in order
"""

import json
import os
from .document_classifier_agent import DocumentClassifierAgent
from .api_testing_agent import APITestingAgent


def run_workflow(docs_dir: str, postman_collection_path: str, 
                 postman_env_path: str, output_dir: str):
    """
    Main workflow function
    
    docs_dir: Folder with your documents
    postman_collection_path: Path to your .postman_collection.json file
    postman_env_path: Path to your environment file (or None)
    output_dir: Where to save the results
    
    Returns: Dictionary with results
    """
    
    print("\n" + "="*70)
    print("🤖 MULTI-AGENT WORKFLOW")
    print("="*70)
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ Error: GOOGLE_API_KEY not found in environment")
        return {"success": False, "error": "Missing API key"}
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # ============================================================
    # STEP 1: Document Classification
    # ============================================================
    print("\n📋 STEP 1: CLASSIFYING DOCUMENTS")
    print("-" * 70)
    
    try:
        # Create the document classifier agent
        classifier = DocumentClassifierAgent(api_key=api_key)
        
        # Run classification
        cache_file = os.path.join(output_dir, "document_classifications.json")
        doc_map = classifier.classify_documents(docs_dir, cache_file)
        
        print(f"\n✅ Step 1 Complete: Classified {len(doc_map)} documents")
        
    except Exception as e:
        print(f"\n❌ Step 1 Failed: {e}")
        return {"success": False, "error": str(e), "step": 1}
    
    # ============================================================
    # STEP 2: API Testing
    # ============================================================
    print("\n\n🧪 STEP 2: TESTING APIs")
    print("-" * 70)
    
    try:
        # Create the API testing agent
        api_tester = APITestingAgent(api_key=api_key)
        
        # Give it the document classifications
        api_tester.set_documents(doc_map)
        
        # Load environment variables if provided
        if postman_env_path and os.path.exists(postman_env_path):
            with open(postman_env_path, "r") as f:
                env_data = json.load(f)
                env_vars = {}
                for var in env_data.get("values", []):
                    if var.get("enabled", True):
                        env_vars[var["key"]] = var.get("value", "")
                api_tester.set_environment(env_vars)
        
        # Test the APIs
        results = api_tester.test_apis(postman_collection_path)
        
        print(f"\n✅ Step 2 Complete: Tested {len(results)} APIs")
        
    except Exception as e:
        print(f"\n❌ Step 2 Failed: {e}")
        return {"success": False, "error": str(e), "step": 2}
    
    # ============================================================
    # STEP 3: Generate Report
    # ============================================================
    print("\n\n📊 STEP 3: GENERATING REPORT")
    print("-" * 70)
    
    try:
        # Create a simplified report
        report = []
        
        for result in results:
            api_entry = {
                "apiName": result["api_name"],
                "method": result.get("method", "POST"),
                "url": result.get("url", ""),
                "correctFiles": [],
                "failedFiles": []
            }
            
            # Check initial result
            if result["success"]:
                api_entry["correctFiles"].append({
                    "fileName": os.path.basename(result["file_used"]),
                    "docType": result.get("document_type", "unknown")
                })
            else:
                api_entry["failedFiles"].append({
                    "nameOfFile": os.path.basename(result["file_used"]),
                    "docType": result.get("document_type", "unknown"),
                    "errorMessage": result.get("error_message", "")[:200]
                })
            
            # Check if retry succeeded
            if result.get("retry_success") and result.get("correct_document"):
                correct_doc = result["correct_document"]
                api_entry["correctFiles"].append({
                    "fileName": os.path.basename(correct_doc),
                    "docType": doc_map[correct_doc].get("document_type", "unknown")
                })
            
            report.append(api_entry)
        
        # Save report
        report_path = os.path.join(output_dir, "report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to: {report_path}")
        
    except Exception as e:
        print(f"\n❌ Step 3 Failed: {e}")
        return {"success": False, "error": str(e), "step": 3}
    
    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE!")
    print("="*70)
    print(f"📁 Documents classified: {len(doc_map)}")
    print(f"🧪 APIs tested: {len(results)}")
    print(f"📊 Report: {report_path}")
    print("="*70 + "\n")
    
    return {
        "success": True,
        "documents_classified": len(doc_map),
        "apis_tested": len(results),
        "report_path": report_path,
        "results": results
    }
