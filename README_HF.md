---
title: Tender Digest AI
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: apache-2.0
---

# Tender Digest AI

🤖 **AI-Powered Global Tender Analysis & Intelligence Platform**

## Features

- **Smart Categorization** - Automatically categorize tenders by industry and type
- **Risk Assessment** - Evaluate tender complexity and competition levels  
- **Key Information Extraction** - Extract important details like deadlines, values, organizations
- **AI Recommendations** - Get actionable insights powered by LangChain and HuggingFace
- **Multi-Document Support** - Analyze up to 10 PDF files simultaneously
- **Beautiful UI** - Professional interface with real-time progress indicators

## Technology Stack

- **Frontend**: Streamlit with custom CSS
- **AI Framework**: LangChain with ConversationalRetrievalChain
- **Models**: HuggingFace (openai/gpt-oss-20b, sentence-transformers)
- **Vector Store**: FAISS for semantic search
- **PDF Processing**: LangChain PyPDFLoader

## Usage

1. Upload PDF tender documents using the sidebar
2. Select analysis options (Quick or Detailed)
3. Click "Start Intelligent Analysis" 
4. View AI-powered insights and recommendations
5. Download detailed analysis reports

## Demo

Try it live: [Tender Digest AI on HuggingFace Spaces](https://huggingface.co/spaces/YOUR_USERNAME/tender-digest-ai)

---

Built with ❤️ using LangChain, HuggingFace, and Streamlit