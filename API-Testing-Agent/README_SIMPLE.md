# 🤖 Simple Multi-Agent System (Beginner-Friendly!)

This project uses **2 simple agents** that work together to test your APIs with the right documents.

## 📚 What Are "Agents"?

Think of agents like little robot helpers. Each one has a specific job:

- **Agent 1 (Document Classifier)**: Looks at all your documents and figures out what type each one is (like "passport", "bank statement", etc.)
- **Agent 2 (API Tester)**: Tests your APIs by sending them documents, and if an API fails, it figures out what document it needs and tries again

## 🎯 What This Does

1. **Step 1**: Agent 1 scans your `documents/` folder and classifies each document using AI
2. **Step 2**: Agent 2 loads your Postman collection and tests each API
3. **Step 3**: Creates a report showing which documents work with which APIs

## 📁 Project Structure

```
API-Testing-Agent/
├── agents/                              # 👈 Your two agents live here
│   ├── document_classifier_agent.py     # Agent 1: Classifies documents
│   ├── api_testing_agent.py             # Agent 2: Tests APIs
│   └── workflow.py                      # The checklist that runs both agents
│
├── run_agents.py                        # 👈 Run this file to start!
├── requirements.txt                     # Python packages needed
├── .env                                 # Your API key goes here
│
├── documents/                           # 👈 Put your documents here
├── collections/                         # 👈 Put your Postman collection here
└── outputs/                             # 👈 Results go here
    ├── document_classifications.json    # What Agent 1 found
    └── report.json                      # Final report
```

## 🚀 How to Run

### 1. Install Python packages

```bash
pip install -r requirements.txt
```

### 2. Set up your API key

Create a file called `.env` and add your Google API key:

```
GOOGLE_API_KEY=your_key_here
```

### 3. Add your files

- Put your documents in the `documents/` folder
- Put your Postman collection in the `collections/` folder

### 4. Run it!

```bash
python run_agents.py
```

That's it! The agents will do their work and create a report.

## 📊 Understanding the Report

The report (`outputs/report.json`) shows:

```json
{
  "apiName": "Upload Passport",
  "correctFiles": [
    {
      "fileName": "john_passport.pdf",
      "docType": "passport"
    }
  ],
  "failedFiles": [
    {
      "nameOfFile": "bank_statement.pdf",
      "docType": "bank_statement",
      "errorMessage": "Wrong document type"
    }
  ]
}
```

- **correctFiles**: Documents that worked with this API ✅
- **failedFiles**: Documents that didn't work ❌

## 🔧 How It Works (Simple Explanation)

### Agent 1: Document Classifier

```python
# What it does:
1. Looks at each file in documents/ folder
2. Sends it to Google's Gemini AI
3. Gemini looks at the file and says "this is a passport" or "this is a bank statement"
4. Saves the results so we don't have to do it again
```

### Agent 2: API Tester

```python
# What it does:
1. Reads your Postman collection
2. Picks a random document and tries it with an API
3. If it fails, asks Gemini "what went wrong?"
4. Finds the right document and tries again
5. Remembers what worked for each API
```

### How They Work Together

```
┌─────────────────┐
│  run_agents.py  │  ← You run this
└────────┬────────┘
         │
         ├─► Agent 1: Classify all documents
         │   Result: {"passport.pdf": "passport", "bank.pdf": "bank_statement"}
         │
         ├─► Agent 2: Test APIs with those documents
         │   - Try random document → fails
         │   - Ask Gemini what's needed
         │   - Find correct document → success!
         │
         └─► Save report
```

## 💡 Key Concepts for Beginners

### What is an Agent?

An **agent** is just a Python class that:
- Has some data (like `self.doc_map`)
- Has some functions (like `classify_documents()`)
- Does work automatically

### What is "Communication Between Agents"?

It's simple! Agent 1 creates a dictionary of results, and Agent 2 uses that dictionary:

```python
# Agent 1 creates this:
doc_map = {
    "passport.pdf": {"type": "passport"},
    "bank.pdf": {"type": "bank_statement"}
}

# Agent 2 uses it:
api_tester.set_documents(doc_map)  # Now Agent 2 knows about the documents!
```

### Why Use Agents?

Instead of one big messy script, we split the work:
- Agent 1 only worries about documents
- Agent 2 only worries about APIs
- Each one is easier to understand and fix!

## 🆘 Troubleshooting

### "GOOGLE_API_KEY not found"
→ Make sure you created a `.env` file with your API key

### "Can't find folder: documents"
→ Create a `documents/` folder and add some files

### "Classification failed"
→ Make sure your document is a readable format (PDF, JPG, PNG)

## 📝 Making Changes

Want to modify something? Here's where to look:

- **Change how documents are classified**: Edit `agents/document_classifier_agent.py`
- **Change how APIs are tested**: Edit `agents/api_testing_agent.py`
- **Change the workflow steps**: Edit `agents/workflow.py`
- **Change settings (folders, etc.)**: Edit `run_agents.py`

## 🎓 Learning More

This project uses:
- **Python classes** for organizing code into agents
- **Google Gemini AI** for understanding documents and errors
- **Dictionaries** for passing data between agents
- **Functions** for breaking down big tasks into small steps

No complex frameworks needed! Just simple, readable Python. 🐍
