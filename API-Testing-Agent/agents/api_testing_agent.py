"""
Simple API Testing Agent

What this does:
- Takes a Postman collection (list of APIs)
- Tests each API with documents we classified
- If an API fails, figures out what document type it needs
- Tries again with the correct document

Think of it like: Agent tries to match the right document to each API
"""

import json
import mimetypes
import os
import random
import re
import requests
import google.generativeai as genai


class APITestingAgent:
    """A simple agent that tests APIs with documents"""
    
    def __init__(self, api_key: str):
        """
        Set up the agent
        
        api_key: Your Google API key to use Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.doc_map = {}  # Will store document classifications
        self.env_vars = {}  # Will store environment variables
    
    def set_documents(self, doc_map: dict):
        """
        Give the agent the document classifications
        
        doc_map: Dictionary from classifier agent with format:
                 {"file_path": {"document_type": "passport", "confidence": 0.95}}
        """
        self.doc_map = doc_map
    
    def set_environment(self, env_vars: dict):
        """
        Set Postman environment variables (like {{base_url}})
        
        env_vars: Dictionary like {"base_url": "http://localhost:8000"}
        """
        self.env_vars = env_vars
    
    def test_apis(self, postman_collection_path: str):
        """
        Main function: Test all APIs from a Postman collection
        
        postman_collection_path: Path to your .postman_collection.json file
        
        Returns: List of test results
        """
        # Step 1: Load the Postman collection
        with open(postman_collection_path, "r") as f:
            collection = json.load(f)
        
        # Step 2: Find APIs that need file uploads
        all_apis = self._find_all_apis(collection)
        upload_apis = [api for api in all_apis if self._needs_file_upload(api)]
        
        print(f"\n📋 Found {len(upload_apis)} APIs that need file uploads\n")
        
        # Step 3: Test each API
        results = []
        used_documents = set()  # Track which docs we've successfully used
        
        for api in upload_apis:
            api_name = api.get("name", "unnamed")
            print(f"🧪 Testing: {api_name}")
            
            # Pick a random document that we haven't used yet
            available_docs = {path: info for path, info in self.doc_map.items() 
                            if path not in used_documents}
            
            if not available_docs:
                print("  ⚠️  No more documents available\n")
                continue
            
            random_file = random.choice(list(available_docs.keys()))
            doc_info = available_docs[random_file]
            
            print(f"  📄 Trying: {os.path.basename(random_file)}")
            print(f"     Type: {doc_info.get('document_type', 'unknown')}")
            
            # Test the API with this document
            result = self._test_one_api(api, random_file, doc_info)
            
            # Check if it worked
            if result["success"]:
                print(f"  ✅ Success!\n")
                used_documents.add(random_file)
            else:
                # It failed - let's try to understand why
                print(f"  ❌ Failed: {result['error_message'][:100]}...")
                
                # Ask Gemini what document type this API needs
                required_type = self._ask_gemini_what_went_wrong(result)
                
                if required_type:
                    print(f"  💡 API needs: {required_type}")
                    
                    # Find a document of that type
                    matching_doc = self._find_document_by_type(required_type)
                    
                    if matching_doc:
                        print(f"  🔄 Retrying with: {os.path.basename(matching_doc)}")
                        retry_result = self._test_one_api(api, matching_doc, self.doc_map[matching_doc])
                        
                        if retry_result["success"]:
                            print(f"  ✅ Retry succeeded!\n")
                            used_documents.add(matching_doc)
                            result["retry_success"] = True
                            result["correct_document"] = matching_doc
                        else:
                            print(f"  ❌ Retry also failed\n")
                    else:
                        print(f"  ⚠️  No {required_type} document found\n")
                else:
                    print(f"  ⚠️  Couldn't determine what went wrong\n")
            
            results.append(result)
        
        return results
    
    def _test_one_api(self, api_config: dict, file_path: str, doc_info: dict):
        """
        Internal helper: Test one API endpoint with one document
        """
        try:
            # Build the HTTP request
            method, url, headers, body_data = self._build_request(api_config, file_path)
            
            # Send the request
            if body_data.get("files"):
                response = requests.request(method, url, headers=headers, 
                                          files=body_data["files"], timeout=30)
            elif body_data.get("content"):
                response = requests.request(method, url, headers=headers, 
                                          data=body_data["content"], timeout=30)
            else:
                response = requests.request(method, url, headers=headers, timeout=30)
            
            # Check if successful
            success = response.status_code in [200, 201, 204]
            
            return {
                "api_name": api_config.get("name", "unnamed"),
                "method": method,
                "url": url,
                "file_used": file_path,
                "document_type": doc_info.get("document_type"),
                "success": success,
                "status_code": response.status_code,
                "error_message": response.text if not success else "",
                "response_headers": dict(response.headers)
            }
            
        except Exception as e:
            return {
                "api_name": api_config.get("name", "unnamed"),
                "file_used": file_path,
                "success": False,
                "error_message": str(e)
            }
    
    def _build_request(self, api_config: dict, file_path: str):
        """
        Internal helper: Convert Postman format to Python requests format
        """
        request_data = api_config["request"]
        method = request_data.get("method", "POST")
        
        # Get URL and replace {{variables}}
        url_data = request_data.get("url")
        if isinstance(url_data, dict):
            url = url_data.get("raw", "")
        else:
            url = str(url_data)
        url = self._replace_variables(url)
        
        # Get headers
        headers = {}
        for header in request_data.get("header", []):
            if header.get("key"):
                headers[header["key"]] = self._replace_variables(header.get("value", ""))
        
        # Build body with file
        body = request_data.get("body", {})
        mode = body.get("mode")
        
        files_data = None
        content_data = None
        
        if mode == "formdata":
            # Form with multiple fields
            fields = []
            for field in body.get("formdata", []):
                key = field.get("key")
                field_type = field.get("type")
                
                if field_type == "file":
                    # This is where we attach our document
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    
                    # Figure out the file type (MIME type)
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if not mime_type:
                        # Common types
                        ext = os.path.splitext(file_path)[1].lower()
                        mime_types = {
                            '.pdf': 'application/pdf',
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png'
                        }
                        mime_type = mime_types.get(ext, 'application/octet-stream')
                    
                    fields.append((key, (os.path.basename(file_path), file_content, mime_type)))
                else:
                    # Regular text field
                    value = self._replace_variables(field.get("value", ""))
                    fields.append((key, value))
            
            files_data = fields
        
        elif mode in ("file", "binary"):
            # Raw file upload
            with open(file_path, "rb") as f:
                content_data = f.read()
        
        return method, url, headers, {"files": files_data, "content": content_data}
    
    def _replace_variables(self, text: str):
        """
        Replace {{variable_name}} with actual values
        Example: {{base_url}}/upload becomes http://localhost:8000/upload
        """
        def replacer(match):
            var_name = match.group(1)
            return self.env_vars.get(var_name, match.group(0))
        
        return re.sub(r"{{([^}]+)}}", replacer, text)
    
    def _find_all_apis(self, collection: dict):
        """
        Internal helper: Extract all API requests from Postman collection
        (Postman can have nested folders, so we need to search recursively)
        """
        apis = []
        
        def search(node):
            if isinstance(node, dict):
                if "request" in node:
                    # This is an API
                    apis.append(node)
                if "item" in node:
                    # This is a folder, search inside
                    for item in node["item"]:
                        search(item)
        
        search(collection)
        return apis
    
    def _needs_file_upload(self, api: dict):
        """
        Internal helper: Check if an API needs a file upload
        """
        try:
            body = api["request"].get("body", {})
            mode = body.get("mode")
            
            if mode in ("file", "binary"):
                return True
            
            if mode == "formdata":
                # Check if any field is a file
                for field in body.get("formdata", []):
                    if field.get("type") == "file":
                        return True
            
            return False
        except:
            return False
    
    def _ask_gemini_what_went_wrong(self, error_result: dict):
        """
        Internal helper: Use Gemini AI to understand what document the API needs
        """
        try:
            # Read the prompt that tells Gemini how to parse errors
            with open("prompts/normalize_error.md", "r") as f:
                instructions = f.read()
            
            # Prepare error information for Gemini
            error_info = json.dumps({
                "status": error_result.get("status_code"),
                "body": error_result.get("error_message", "")[:1000]
            })
            
            # Ask Gemini
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content([
                instructions,
                "\n\nError to analyze:\n",
                error_info
            ])
            
            # Extract the answer
            text = response.text.strip()
            
            # Find JSON in response
            json_match = re.search(r"{[\s\S]*}", text)
            if json_match:
                result = json.loads(json_match.group(0))
                return result.get("required_document_type")
            
            return None
            
        except Exception as e:
            print(f"    (Couldn't analyze error: {e})")
            return None
    
    def _find_document_by_type(self, doc_type: str):
        """
        Internal helper: Find a document that matches the required type
        """
        doc_type_lower = doc_type.lower()
        
        for file_path, info in self.doc_map.items():
            classified_type = info.get("document_type", "").lower()
            if doc_type_lower in classified_type or classified_type in doc_type_lower:
                return file_path
        
        return None
