"""
Simple Document Classifier Agent

What this does:
- Looks at all documents in a folder
- Uses Google's Gemini AI to understand what type of document it is
- Saves the results so we don't have to do it again

Think of it like: Agent goes through your documents and labels each one
"""

import json
import os
import re
import google.generativeai as genai


class DocumentClassifierAgent:
    """A simple agent that classifies documents"""
    
    def __init__(self, api_key: str):
        """
        Set up the agent
        
        api_key: Your Google API key to use Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.cache = {}  # Remember files we already uploaded
    
    def classify_documents(self, docs_dir: str, cache_file: str = None):
        """
        Main function: Classify all documents in a folder
        
        docs_dir: Folder with your documents
        cache_file: File to save results (so we don't re-do work)
        
        Returns: A dictionary like {"file_path": {"type": "passport", "confidence": 0.95}}
        """
        results = {}
        
        # Step 1: Try to load previous results if they exist
        if cache_file and os.path.exists(cache_file):
            print(f"📂 Loading saved results from {cache_file}")
            with open(cache_file, "r") as f:
                results = json.load(f)
            print(f"✓ Found {len(results)} previous results")
        
        # Step 2: Find all document files
        all_files = []
        for root, _, files in os.walk(docs_dir):
            for filename in files:
                # Skip hidden files and markdown files
                if not filename.startswith(".") and not filename.endswith(".md"):
                    full_path = os.path.join(root, filename)
                    all_files.append(full_path)
        
        print(f"\n📄 Found {len(all_files)} documents total")
        
        # Step 3: Classify only new documents (ones we haven't seen before)
        new_files = [f for f in all_files if f not in results]
        
        if new_files:
            print(f"🔍 Classifying {len(new_files)} new documents...\n")
            
            for file_path in new_files:
                filename = os.path.basename(file_path)
                print(f"  Processing: {filename}...", end=" ")
                
                # Ask Gemini to classify this document
                classification = self._ask_gemini_to_classify(file_path)
                
                if classification:
                    results[file_path] = classification
                    doc_type = classification.get("document_type", "unknown")
                    confidence = classification.get("confidence", 0)
                    print(f"✓ {doc_type} (confidence: {confidence:.0%})")
                else:
                    results[file_path] = {"document_type": "failed", "confidence": 0.0}
                    print("✗ failed")
        else:
            print("✓ All documents already classified!\n")
        
        # Step 4: Save results to cache file
        if cache_file:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Saved results to {cache_file}")
        
        return results
    
    def _ask_gemini_to_classify(self, file_path: str):
        """
        Internal helper: Send a file to Gemini and ask what type it is
        """
        try:
            # Step 1: Upload the file to Gemini
            file_obj = self._upload_file(file_path)
            
            # Step 2: Read our prompt that tells Gemini what to do
            prompt_file = "prompts/classify_document.md"
            with open(prompt_file, "r") as f:
                instructions = f.read()
            
            # Step 3: Create a Gemini model and ask it
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content([
                instructions,
                "\n\nClassify this file and return only JSON.",
                file_obj
            ])
            
            # Step 4: Extract the JSON response
            response_text = response.text.strip()
            
            # Find JSON in the response (it's between { and })
            json_match = re.search(r"\{[\s\S]*\}", response_text)
            if json_match:
                classification = json.loads(json_match.group(0))
                return classification
            
            return None
            
        except Exception as e:
            print(f"\n  Error: {e}")
            return None
    
    def _upload_file(self, file_path: str):
        """
        Internal helper: Upload a file to Gemini (with caching to avoid re-uploads)
        """
        # Check if we already uploaded this file
        if file_path in self.cache:
            return self.cache[file_path]
        
        # Upload it
        file_obj = genai.upload_file(file_path)
        
        # Remember it for next time
        self.cache[file_path] = file_obj
        
        return file_obj
