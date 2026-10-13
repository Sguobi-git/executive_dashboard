# Executive Dashboard Demo

A demo variant of the [Sheet Q&A service](https://github.com/Sguobi-git/ai-chatbot-service), built for a live stakeholder presentation at Expo Convention Contractors (Miami).

## What this is, specifically

Same underlying idea as the Sheet Q&A service: a Flask backend that answers natural-language questions against a live Google Sheet using `sentence-transformers` embeddings to find the closest matching column and row. No LLM, no vector database, no real RAG pipeline.

For this version, a handful of questions I expected to be asked in the demo (status overview, budget, performance) are answered with pre-written response templates in `sheet_qa.py` instead of being computed live, so the answers would be fast and polished in front of an audience. That's a live-demo shortcut, not a claim that the system generates financial analysis or recommendations; the specific figures in those canned responses are placeholders from the demo data, not real numbers. Anything outside those few anticipated questions falls back to the same embedding-based column/row lookup as the base service.

If you want the real, non-scripted version of this logic, see [ai-chatbot-service](https://github.com/Sguobi-git/ai-chatbot-service).

## Stack

Python, Flask, sentence-transformers, pandas, a React-based static front end.

## Running it

```
pip install -r requirements.txt
export GOOGLE_SHEETS_URL=<your Google Apps Script web app URL>
python app.py
```
