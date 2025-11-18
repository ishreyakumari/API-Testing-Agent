"""
Simple Multi-Agent Runner

This is the main script you run to start everything!

What it does:
1. Loads your settings (API key, folders, etc.)
2. Runs Agent 1: Classify all documents
3. Runs Agent 2: Test APIs with those documents
4. Creates a report showing what worked and what didn't

How to use:
    python run_agents.py

Before running:
    Make sure you have GOOGLE_API_KEY in your .env file
"""

import os
import sys
from dotenv import load_dotenv
from agents.workflow import run_workflow


def main():
    """Main function - this is what runs when you start the script"""
    
    # Step 1: Load environment variables (like your API key)
    load_dotenv()
    
    # Step 2: Check that we have the API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found!")
        print("💡 Tip: Add it to your .env file")
        sys.exit(1)
    
    # Step 3: Set up your folders and files
    DOCS_DIR = "documents"  # Where your documents are
    POSTMAN_COLLECTION = "collections/sk-api.postman_collection.json"  # Your API collection
    POSTMAN_ENV = None  # Optional: environment variables file
    OUTPUT_DIR = "outputs"  # Where to save results
    
    # Step 4: Make sure the folders exist
    if not os.path.exists(DOCS_DIR):
        print(f"❌ Error: Can't find folder: {DOCS_DIR}")
        sys.exit(1)
    
    if not os.path.exists(POSTMAN_COLLECTION):
        print(f"❌ Error: Can't find file: {POSTMAN_COLLECTION}")
        sys.exit(1)
    
    # Step 5: Show what we're about to do
    print("\n🚀 Starting the Agents!")
    print(f"📁 Looking at documents in: {DOCS_DIR}")
    print(f"📋 Testing APIs from: {POSTMAN_COLLECTION}")
    print(f"📊 Will save results to: {OUTPUT_DIR}")
    
    # Step 6: Run the workflow (this is where the magic happens!)
    try:
        result = run_workflow(
            docs_dir=DOCS_DIR,
            postman_collection_path=POSTMAN_COLLECTION,
            postman_env_path=POSTMAN_ENV,
            output_dir=OUTPUT_DIR
        )
        
        # Step 7: Check if everything worked
        if result.get("success"):
            print(f"\n🎉 All done! Check your report at:")
            print(f"   {result['report_path']}")
            return 0
        else:
            print(f"\n😕 Something went wrong:")
            print(f"   {result.get('error', 'Unknown error')}")
            return 1
    
    except KeyboardInterrupt:
        # User pressed Ctrl+C
        print("\n\n⚠️  Stopped by user (Ctrl+C)")
        return 130
    
    except Exception as e:
        # Something unexpected happened
        print(f"\n❌ Error: {e}")
        
        # Show more details for debugging
        import traceback
        traceback.print_exc()
        return 1


# This runs the main function when you run the script
if __name__ == "__main__":
    sys.exit(main())
