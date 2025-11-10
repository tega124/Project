# tasks4 — OpenAI Chat Summarizer

This standalone experiment demonstrates using the **OpenAI Chat Completions API** to summarize paragraph-length task descriptions into short, actionable phrases.  
It builds on previous tasks (`tasks1–tasks3`) but runs independently.

## 🧠 Features
- Uses the `gpt-5-mini` model via the `OpenAI` Python SDK  
- Reads multiple paragraph inputs and summarizes each into a 3–7 word phrase  
- Includes two built-in sample task descriptions  
- Can read additional input from files or standard input (stdin)

## ⚙️ Setup
1. Make sure your `.env` file contains:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
