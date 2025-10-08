import streamlit as st
import PyPDF2
import io
import re
import os
from datetime import datetime
import json
import base64
from typing import List, Dict, Any
import time
import warnings
warnings.filterwarnings('ignore')

# AI/ML imports with error handling (updated imports)
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import Document
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI modules not available: {e}")
    AI_AVAILABLE = False

# Set page config
st.set_page_config(
    page_title="Tender Digest AI - Global Tender Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deployment optimizations
@st.cache_resource
def load_embeddings():
    """Load embeddings with caching for deployment optimization"""
    if not AI_AVAILABLE:
        return None
    try:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    except Exception as e:
        st.error(f"Failed to load embeddings: {e}")
        return None

@st.cache_resource
def load_llm():
    """Load LLM with caching and error handling"""
    if not AI_AVAILABLE:
        return None
    try:
        # Original model with deployment optimizations
        repo_id = "openai/gpt-oss-20b"
        llm = HuggingFaceEndpoint(
            repo_id=repo_id,
            max_length=1024,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            typical_p=0.95,
            repetition_penalty=1.03,
            timeout=60,  # Increased timeout for larger model
            model_kwargs={
                "max_new_tokens": 512,
                "return_full_text": False
            }
        )
        return ChatHuggingFace(llm=llm)
    except Exception as e:
        st.warning(f"Primary model unavailable, trying fallback: {e}")
        # Fallback to smaller model
        try:
            repo_id = "microsoft/DialoGPT-medium"
            llm = HuggingFaceEndpoint(
                repo_id=repo_id,
                max_length=512,
                temperature=0.5,
                timeout=30
            )
            return ChatHuggingFace(llm=llm)
        except Exception as e2:
            st.error(f"All models unavailable: {e2}")
            return None

# Global variables for caching
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'llm' not in st.session_state:
    st.session_state.llm = None

# Enhanced CSS with modern styling and animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 3.5rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        position: relative;
        z-index: 2;
    }
    .main-header p {
        color: rgba(255,255,255,0.95);
        text-align: center;
        margin: 1rem 0 0 0;
        font-size: 1.3rem;
        font-weight: 400;
        position: relative;
        z-index: 2;
    }
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    .metric-card h3 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .metric-card p {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .analysis-result {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(40, 167, 69, 0.2);
        box-shadow: 0 8px 32px rgba(40, 167, 69, 0.1);
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .upload-section {
        border: 3px dashed rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
        margin: 2rem 0;
        transition: all 0.3s ease;
        position: relative;
    }
    .upload-section:hover {
        border-color: #667eea;
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
    }
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        animation: slideIn 0.5s ease;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .document-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .document-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header with Statistics
st.markdown("""
<div class="main-header">
    <h1>� Tender Digest AI</h1>
    <p>Advanced Global Tender Analysis & Intelligence Platform</p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">⚡</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Lightning Fast</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">🎯</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Smart Analysis</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">📊</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Rich Insights</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">🌍</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Global Support</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

class TenderAnalyzer:
    """Original LangChain-based tender analysis with HuggingFace models"""
    
    def __init__(self):
        self.embeddings = None
        self.llm = None
        self.vectorstore = None
        self.conversation_chain = None
        
        # Initialize models
        self.load_models()
    
    def load_models(self):
        """Load LangChain models and embeddings with optimization"""
        try:
            # Use cached models if available
            if st.session_state.embeddings is None:
                st.info("🔄 Loading AI embeddings... This may take a moment.")
                st.session_state.embeddings = load_embeddings()
            
            if st.session_state.llm is None:
                st.info("🤖 Loading AI language model... This may take a moment.")
                st.session_state.llm = load_llm()
            
            # Use cached models
            self.embeddings = st.session_state.embeddings
            self.llm = st.session_state.llm
            
            if self.embeddings and self.llm:
                st.success("✅ AI models loaded successfully!")
                return True
            else:
                st.warning("⚠️ Some AI models failed to load. Analysis may be limited.")
                return False
            
        except Exception as e:
            st.error(f"Failed to load AI models: {e}")
            st.info("Please check your internet connection and try again.")
            return False
    
    def process_multiple_pdfs(self, uploaded_files):
        """Process multiple PDF files and create vector store"""
        try:
            documents = []
            
            for uploaded_file in uploaded_files:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Load PDF using LangChain
                loader = PyPDFLoader(temp_path)
                docs = loader.load()
                
                # Add metadata
                for doc in docs:
                    doc.metadata['filename'] = uploaded_file.name
                
                documents.extend(docs)
                
                # Clean up temp file
                os.remove(temp_path)
            
            if not documents:
                st.error("No documents could be processed")
                return False
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            splits = text_splitter.split_documents(documents)
            
            # Create vector store
            if self.embeddings:
                self.vectorstore = FAISS.from_documents(splits, self.embeddings)
                
                # Create conversation chain
                memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
                
                self.conversation_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                    memory=memory,
                    return_source_documents=True
                )
                
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error processing PDFs: {e}")
            return False
    
    def analyze_text_smart(self, query: str) -> Dict[str, Any]:
        """Smart analysis using LangChain and LLM"""
        if not self.conversation_chain:
            return {"error": "Analysis chain not initialized"}
        
        try:
            # Enhanced prompts for better analysis
            analysis_queries = {
                "category": f"""
                Analyze this tender document and categorize it. Consider these categories:
                - Construction & Infrastructure
                - IT & Software Development  
                - Medical & Healthcare
                - Transportation & Logistics
                - Education & Training
                - Security & Surveillance
                - Maintenance & Services
                - Supply & Procurement
                - Consulting & Advisory
                - Legal & Compliance
                
                Question: What is the primary category of this tender? Provide category and confidence level.
                Context: {query[:500]}
                """,
                
                "key_info": f"""
                Extract key information from this tender document:
                - Tender number/reference
                - Organization/Department issuing
                - Estimated value/budget
                - Submission deadline
                - Location/area of work
                - Key requirements
                
                Question: What are the key details of this tender?
                Context: {query[:500]}
                """,
                
                "risk_assessment": f"""
                Assess the risk level of this tender considering:
                - Technical complexity
                - Time constraints
                - Financial requirements
                - Competition level
                - Compliance requirements
                
                Question: What is the risk level (High/Medium/Low) and why?
                Context: {query[:500]}
                """,
                
                "recommendations": f"""
                Based on this tender analysis, provide 5-8 actionable recommendations for potential bidders:
                - Preparation strategies
                - Key focus areas
                - Risk mitigation
                - Competitive advantages
                
                Question: What are the top recommendations for this tender?
                Context: {query[:500]}
                """
            }
            
            results = {}
            
            # Run analysis queries
            for analysis_type, analysis_query in analysis_queries.items():
                try:
                    response = self.conversation_chain({
                        "question": analysis_query,
                        "chat_history": []
                    })
                    
                    results[analysis_type] = {
                        "answer": response.get("answer", ""),
                        "sources": [doc.metadata.get('filename', 'Unknown') 
                                  for doc in response.get("source_documents", [])]
                    }
                    
                except Exception as e:
                    results[analysis_type] = {"error": str(e)}
            
            return results
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def enhanced_search(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Enhanced search with source documents"""
        if not self.vectorstore:
            return {"error": "Vector store not initialized"}
        
        try:
            # Similarity search
            docs = self.vectorstore.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content[:300] + "...",
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "page": doc.metadata.get('page', 'Unknown')
                })
            
            return {"results": results}
            
        except Exception as e:
            return {"error": f"Search failed: {e}"}

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""

    def analyze_tender_category(self, text: str) -> Dict[str, Any]:
        """Categorize tender based on keywords"""
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in self.tender_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[primary_category] / len(self.tender_keywords[primary_category])
            return {
                'primary_category': primary_category.replace('_', ' ').title(),
                'confidence': min(confidence * 100, 100),
                'all_categories': category_scores
            }
        else:
            return {
                'primary_category': 'General/Other',
                'confidence': 50,
                'all_categories': {}
            }

    def extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key tender information using regex patterns"""
        info = {
            'tender_number': None,
            'organization': None,
            'estimated_value': None,
            'deadline': None,
            'location': None
        }
        
        # Tender number patterns
        tender_patterns = [
            r'tender\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
            r'ref\.?\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
            r'notice\s+no\.?\s*:?\s*([A-Z0-9/\-]+)'
        ]
        
        for pattern in tender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['tender_number'] = match.group(1)
                break
        
        # Organization patterns
        org_patterns = [
            r'issued\s+by\s*:?\s*([A-Za-z\s,]+?)(?:\n|$)',
            r'organization\s*:?\s*([A-Za-z\s,]+?)(?:\n|$)',
            r'department\s*:?\s*([A-Za-z\s,]+?)(?:\n|$)'
        ]
        
        for pattern in org_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['organization'] = match.group(1).strip()[:100]
                break
        
        # Value extraction
        for pattern in self.value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['estimated_value'] = match.group(0)
                break
        
        # Date patterns
        date_patterns = [
            r'last\s+date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'deadline\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due\s+date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['deadline'] = match.group(1)
                break
        
        return info

    def assess_competition_level(self, text: str) -> Dict[str, Any]:
        """Assess competition level based on text analysis"""
        text_lower = text.lower()
        
        high_competition_indicators = [
            'open tender', 'public tender', 'competitive bidding',
            'lowest bidder', 'technical and financial bid'
        ]
        
        low_competition_indicators = [
            'limited tender', 'restricted tender', 'single source',
            'empanelled vendors', 'pre-qualified'
        ]
        
        high_score = sum(1 for indicator in high_competition_indicators if indicator in text_lower)
        low_score = sum(1 for indicator in low_competition_indicators if indicator in text_lower)
        
        if high_score > low_score:
            level = "High"
            confidence = min((high_score / len(high_competition_indicators)) * 100, 100)
        elif low_score > high_score:
            level = "Low"
            confidence = min((low_score / len(low_competition_indicators)) * 100, 100)
        else:
            level = "Medium"
            confidence = 60
        
        return {
            'level': level,
            'confidence': confidence,
            'indicators_found': high_score + low_score
        }

    def calculate_risk_score(self, text: str) -> Dict[str, Any]:
        """Calculate risk score based on risk indicators"""
        text_lower = text.lower()
        risk_count = sum(1 for indicator in self.risk_indicators if indicator in text_lower)
        
        risk_score = min((risk_count / len(self.risk_indicators)) * 100, 100)
        
        if risk_score < 30:
            risk_level = "Low"
        elif risk_score < 60:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            'score': risk_score,
            'level': risk_level,
            'indicators_found': risk_count
        }

    def generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Category-based recommendations
        category = analysis_results.get('category', {}).get('primary_category', '').lower()
        
        if 'construction' in category:
            recommendations.extend([
                "Ensure compliance with safety standards and building codes",
                "Verify contractor credentials and past performance",
                "Consider environmental impact assessments"
            ])
        elif 'it' in category or 'software' in category:
            recommendations.extend([
                "Evaluate technical specifications and scalability",
                "Check for cybersecurity compliance requirements",
                "Assess vendor support and maintenance capabilities"
            ])
        elif 'medical' in category:
            recommendations.extend([
                "Verify regulatory approvals and certifications",
                "Check warranty and after-sales service terms",
                "Ensure compliance with medical device standards"
            ])
        
        # Competition-based recommendations
        competition = analysis_results.get('competition', {})
        if competition.get('level') == 'High':
            recommendations.append("Prepare a competitive bid with detailed technical proposal")
        elif competition.get('level') == 'Low':
            recommendations.append("Focus on meeting specific requirements rather than lowest price")
        
        # Risk-based recommendations
        risk = analysis_results.get('risk', {})
        if risk.get('level') == 'High':
            recommendations.extend([
                "Conduct thorough due diligence before bidding",
                "Consider consortium or partnership for risk sharing"
            ])
        
        # General recommendations
        recommendations.extend([
            "Review all terms and conditions carefully",
            "Prepare necessary documentation in advance",
            "Consider site visits if applicable"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations

def main():
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = TenderAnalyzer()
    
    # Enhanced Sidebar
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h3>📤 Upload Documents</h3>
        <p>Drag & drop up to 10 PDF files</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader with enhanced styling
    uploaded_files = st.sidebar.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Select multiple PDF files (max 10)"
    )
    
    # Limit files
    if uploaded_files and len(uploaded_files) > 10:
        st.sidebar.warning("⚠️ Maximum 10 files allowed. Using first 10 files.")
        uploaded_files = uploaded_files[:10]
    
    # Analysis options
    st.sidebar.markdown("### ⚙️ Analysis Options")
    analysis_depth = st.sidebar.selectbox(
        "Analysis Depth",
        ["Quick Analysis", "Detailed Analysis"],
        help="Quick for basic info, Detailed for comprehensive analysis"
    )
    
    include_recommendations = st.sidebar.checkbox(
        "Include Recommendations",
        value=True,
        help="Generate actionable recommendations"
    )
    
    # Main content with enhanced UI
    if uploaded_files:
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #667eea; font-weight: 700;">📄 Documents Ready for Analysis</h2>
            <p style="color: #6c757d; font-size: 1.1rem;">{len(uploaded_files)} files uploaded successfully</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced document display with hover effects
        cols = st.columns(min(len(uploaded_files), 4))
        for i, file in enumerate(uploaded_files):
            with cols[i % 4]:
                file_size_mb = file.size / (1024 * 1024)
                size_display = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file.size / 1024:.1f} KB"
                
                st.markdown(f"""
                <div class="document-card">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 2.5rem; color: #667eea; margin-bottom: 0.5rem;">📄</div>
                        <h4 style="margin: 0; color: #2c3e50; font-weight: 600;">{file.name[:20]}{'...' if len(file.name) > 20 else ''}</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;">📊 {size_display}</p>
                        <div style="margin-top: 0.5rem; padding: 0.25rem 0.75rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px; display: inline-block;">
                            <span style="color: #667eea; font-size: 0.8rem; font-weight: 500;">✓ Ready</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced Analysis Button
        st.markdown("<div style='text-align: center; margin: 2rem 0;'>", unsafe_allow_html=True)
        analyze_button = st.button(
            "🚀 Start Intelligent Analysis", 
            type="primary",
            help="Click to analyze all uploaded documents with AI-powered insights"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        if analyze_button:
            # Process PDFs with AI
            st.markdown("""
            <div class="progress-container">
                <h4 style="text-align: center; color: #667eea; margin-bottom: 1rem;">
                    🤖 AI-Powered Analysis in Progress...
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Process PDFs and create vector store
            status_text.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin: 1rem 0;">
                <h5 style="color: #667eea; margin: 0;">� Processing Documents with LangChain...</h5>
                <p style="color: #6c757d; margin: 0.5rem 0 0 0;">Creating vector embeddings for intelligent analysis</p>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(0.3)
            
            # Process PDFs
            if st.session_state.analyzer.process_multiple_pdfs(uploaded_files):
                progress_bar.progress(0.6)
                
                # Step 2: Perform AI analysis
                status_text.markdown("""
                <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin: 1rem 0;">
                    <h5 style="color: #667eea; margin: 0;">🧠 Running AI Analysis...</h5>
                    <p style="color: #6c757d; margin: 0.5rem 0 0 0;">Generating insights with HuggingFace models</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Combine all document text for analysis
                combined_text = ""
                for file in uploaded_files:
                    # This would be replaced with proper document retrieval
                    combined_text += f"Document: {file.name}\n"
                
                # Run AI analysis
                ai_results = st.session_state.analyzer.analyze_text_smart(combined_text[:2000])  # Limit for performance
                progress_bar.progress(1.0)
                
                # Format results for display
                all_results = []
                for i, file in enumerate(uploaded_files):
                    result = {
                        'filename': file.name,
                        'ai_analysis': ai_results,
                        'file_size': file.size,
                        'status': 'completed'
                    }
                    all_results.append(result)
                
            else:
                st.error("Failed to process documents. Please try again.")
                return
            
            # Completion message with animation
            status_text.markdown("""
            <div class="success-message">
                <h4 style="margin: 0;">✅ Analysis Complete!</h4>
                <p style="margin: 0.5rem 0 0 0;">All documents have been successfully analyzed</p>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(1.0)
            
            time.sleep(1)  # Brief pause for user experience
            
            # Enhanced Results Header
            st.markdown("""
            <div style="text-align: center; margin: 3rem 0 2rem 0;">
                <h1 style="color: #667eea; font-weight: 700; font-size: 2.5rem;">📊 Intelligent Analysis Results</h1>
                <p style="color: #6c757d; font-size: 1.2rem;">Comprehensive insights from your tender documents</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced Summary metrics with animations
            st.markdown("### 📈 AI Analysis Dashboard")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>Documents Analyzed</p>
                </div>
                """.format(len(all_results)), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>AI</h3>
                    <p>Analysis Mode</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3>✓</h3>
                    <p>LangChain Powered</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <h3>🤖</h3>
                    <p>HuggingFace Models</p>
                </div>
                """, unsafe_allow_html=True)
            
            # AI Analysis Results Display
            st.markdown("### 🤖 AI-Powered Analysis Results")
            
            # Display AI analysis for each category
            if ai_results and not ai_results.get('error'):
                
                # Category Analysis
                if 'category' in ai_results:
                    st.markdown("#### 🏷️ Tender Categorization")
                    category_info = ai_results['category']
                    if not category_info.get('error'):
                        st.markdown(f"""
                        <div class="analysis-result">
                            <p><strong>AI Analysis:</strong></p>
                            <p>{category_info.get('answer', 'Analysis in progress...')}</p>
                            <p><strong>Sources:</strong> {', '.join(category_info.get('sources', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Key Information
                if 'key_info' in ai_results:
                    st.markdown("#### 📋 Key Information Extraction")
                    key_info = ai_results['key_info']
                    if not key_info.get('error'):
                        st.markdown(f"""
                        <div class="analysis-result">
                            <p><strong>AI Analysis:</strong></p>
                            <p>{key_info.get('answer', 'Analysis in progress...')}</p>
                            <p><strong>Sources:</strong> {', '.join(key_info.get('sources', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Risk Assessment
                if 'risk_assessment' in ai_results:
                    st.markdown("#### ⚠️ Risk Assessment")
                    risk_info = ai_results['risk_assessment']
                    if not risk_info.get('error'):
                        st.markdown(f"""
                        <div class="analysis-result">
                            <p><strong>AI Analysis:</strong></p>
                            <p>{risk_info.get('answer', 'Analysis in progress...')}</p>
                            <p><strong>Sources:</strong> {', '.join(risk_info.get('sources', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Recommendations
                if include_recommendations and 'recommendations' in ai_results:
                    st.markdown("#### 💡 AI-Generated Recommendations")
                    rec_info = ai_results['recommendations']
                    if not rec_info.get('error'):
                        st.markdown(f"""
                        <div class="analysis-result">
                            <p><strong>AI Recommendations:</strong></p>
                            <p>{rec_info.get('answer', 'Generating recommendations...')}</p>
                            <p><strong>Sources:</strong> {', '.join(rec_info.get('sources', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            else:
                st.error("AI analysis failed. Please try again.")
            
            # Document Processing Summary
            st.markdown("### 📄 Document Processing Summary")
            for i, result in enumerate(all_results):
                st.markdown(f"""
                <div class="document-card">
                    <h4>📄 {result['filename']}</h4>
                    <p><strong>Size:</strong> {result['file_size'] / 1024:.1f} KB</p>
                    <p><strong>Status:</strong> ✅ {result['status'].title()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Download results
            if st.button("📥 Download Analysis Report"):
                report_data = {
                    'analysis_date': datetime.now().isoformat(),
                    'total_documents': len(all_results),
                    'analysis_type': analysis_depth,
                    'results': all_results
                }
                
                json_str = json.dumps(report_data, indent=2, default=str)
                b64 = base64.b64encode(json_str.encode()).decode()
                
                st.markdown(f"""
                <a href="data:application/json;base64,{b64}" download="tender_analysis_report.json">
                    <button style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px;">
                        📥 Download JSON Report
                    </button>
                </a>
                """, unsafe_allow_html=True)
    
    else:
        # Enhanced Welcome screen
        st.markdown("""
        <div class="upload-section">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
            <h2 style="color: #667eea; font-weight: 700; margin-bottom: 1rem;">Welcome to Tender Digest AI</h2>
            <p style="font-size: 1.1rem; color: #6c757d; margin-bottom: 1.5rem;">
                Transform your tender analysis with intelligent automation
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 1.5rem;">
                <span style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    ⚡ Lightning Fast
                </span>
                <span style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    🎯 AI-Powered
                </span>
                <span style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                    📊 Rich Insights
                </span>
            </div>
            <p style="color: #495057; font-weight: 500;">
                👈 Upload your PDF tender documents using the sidebar to get started
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Feature overview with animations
        st.markdown("### ✨ Powerful Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem; color: #667eea;">🏷️</div>
                </div>
                <h4 style="color: #2c3e50; text-align: center; margin-bottom: 1rem;">Smart Categorization</h4>
                <p style="text-align: center; color: #6c757d; line-height: 1.6;">
                    Automatically categorize tenders by industry, type, and complexity using advanced pattern recognition
                </p>
                <div style="text-align: center; margin-top: 1rem;">
                    <span style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        8+ Categories
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem; color: #667eea;">📊</div>
                </div>
                <h4 style="color: #2c3e50; text-align: center; margin-bottom: 1rem;">Risk Assessment</h4>
                <p style="text-align: center; color: #6c757d; line-height: 1.6;">
                    Evaluate tender complexity, competition levels, and potential risks to make informed bidding decisions
                </p>
                <div style="text-align: center; margin-top: 1rem;">
                    <span style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        Multi-Factor Analysis
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem; color: #667eea;">💡</div>
                </div>
                <h4 style="color: #2c3e50; text-align: center; margin-bottom: 1rem;">Smart Recommendations</h4>
                <p style="text-align: center; color: #6c757d; line-height: 1.6;">
                    Get actionable insights and strategic recommendations tailored to each tender opportunity
                </p>
                <div style="text-align: center; margin-top: 1rem;">
                    <span style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        Actionable Insights
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Info about optimization
        st.markdown("""
        <div class="warning-box">
            <h4>ℹ️ Deployment Optimization</h4>
            <p>This version uses lightweight rule-based analysis for optimal performance on free hosting platforms. 
            It provides fast, accurate results without requiring heavy AI models.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()