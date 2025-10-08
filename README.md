# Tender Analysis AI

A powerful Streamlit-based web application that uses open-source AI models to analyze multiple tender documents simultaneously. Built with LangChain, Streamlit, and Hugging Face models for comprehensive procurement document analysis.

![Tender Analysis AI](https://img.shields.io/badge/AI-Powered-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![LangChain](https://img.shields.io/badge/LangChain-Latest-yellow)

##  Features

- ** Multiple Document Upload**: Upload up to 10 PDF tender documents simultaneously
- ** Cross-Document Analysis**: Analyze and compare requirements across multiple tender documents
- ** Executive Summary Generation**: AI-generated comprehensive summaries covering all uploaded documents
- ** Compliance Requirements Extraction**: Automated extraction of key eligibility and compliance criteria
- ** Interactive Q&A with Sources**: Chat interface with source document references for answers
- ** Document Statistics**: Overview of processed files and text chunks
- ** Global Support**: Works with tender documents from any country or organization
- ** Privacy-First**: All processing done using open-source models via Hugging Face API

##  Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - LLM: OpenAI GPT-OSS-20B (via Hugging Face API)
  - Embeddings: sentence-transformers/all-MiniLM-L6-v2
  - Vector Store: FAISS (in-memory)
- **Document Processing**: PyPDF, LangChain
- **Backend**: Python 3.8+

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- Hugging Face API token (free)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RiddheshMore/Tender-Analysis-AI.git
   cd Tender-Analysis-AI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file in the root directory
   echo 'HUGGINGFACEHUB_API_TOKEN="your_huggingface_token_here"' > .env
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## Usage

1. **Upload Documents**: Select up to 10 PDF tender documents using the file uploader
2. **View Document Overview**: Review statistics showing files processed and text chunks created
3. **Analysis Results**: Get comprehensive executive summary and compliance requirements covering all documents
4. **Interactive Q&A**: Ask specific questions about any of the documents (answers include source references)

### Example Questions You Can Ask:
- "What is the submission deadline?"
- "What are the minimum experience requirements?"
- "What certifications are needed?"
- "What is the project scope?"
- "What are the payment terms?"

##  Project Structure

```
Tender-Analysis-AI/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
└── sample-data/            # Sample tender documents (optional)
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
HUGGINGFACEHUB_API_TOKEN="your_huggingface_token_here"
```

### Getting Hugging Face API Token

1. Go to [Hugging Face](https://huggingface.co/)
2. Sign up for a free account
3. Go to Settings → Access Tokens
4. Create a new token with "Read" permissions
5. Copy and paste it into your `.env` file

## Supported Document Types

- **Government Tenders**: Public procurement documents from any country
- **Corporate RFPs**: Request for Proposals from private companies
- **International Tenders**: Cross-border procurement documents
- **Construction Bids**: Infrastructure and construction project tenders
- **IT/Software Tenders**: Technology procurement documents
- **Service Contracts**: Professional services tender documents

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the existing [Issues](https://github.com/RiddheshMore/Tender-Analysis-AI/issues)
2. Create a new issue with detailed information
3. Join our discussions in the [Discussions](https://github.com/RiddheshMore/Tender-Analysis-AI/discussions) tab

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [LangChain](https://langchain.com/) for the powerful AI orchestration
- [Hugging Face](https://huggingface.co/) for open-source AI models
- [FAISS](https://faiss.ai/) for efficient vector search

---
