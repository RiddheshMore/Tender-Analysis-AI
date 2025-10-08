import os
import streamlit as st
import tempfile
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings, ChatHuggingFace

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Global Tender Analysis AI",
    page_icon="📋",
    layout="wide"
)

@st.cache_resource
def load_models():
    """Load and cache the Hugging Face models."""
    try:
        endpoint = HuggingFaceEndpoint(
            repo_id="openai/gpt-oss-20b",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
        llm = ChatHuggingFace(llm=endpoint)
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        return llm, embeddings
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None

def process_pdfs(uploaded_files):
    """Process uploaded PDF files."""
    all_documents = []
    
    for uploaded_file in uploaded_files:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            
            for doc in documents:
                doc.metadata['source_file'] = uploaded_file.name
            
            all_documents.extend(documents)
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    if all_documents:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return text_splitter.split_documents(all_documents)
    return []

def analyze_text(llm, text, analysis_type):
    """Analyze text using the LLM."""
    try:
        limited_text = text[:3000] if len(text) > 3000 else text
        
        if analysis_type == "summary":
            prompt = f"""Analyze these tender documents and write a comprehensive executive summary:

Document Text:
{limited_text}

Executive Summary:"""
        else:
            prompt = f"""Extract key compliance requirements from these tender documents:

Document Text:
{limited_text}

Key Compliance Requirements:"""
            
        result = llm.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def main():
    st.title("📋 Tender Analysis AI")
    st.subheader("Analyze Multiple Public Procurement Documents")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processed" not in st.session_state:
        st.session_state.processed = False
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose PDF files (up to 10)",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.warning("Maximum 10 files allowed.")
            uploaded_files = uploaded_files[:10]
        
        st.success(f"{len(uploaded_files)} file(s) uploaded")
        
        with st.spinner("Loading models..."):
            llm, embeddings = load_models()
        
        if llm and embeddings:
            with st.spinner("Processing documents..."):
                text_chunks = process_pdfs(uploaded_files)
                
                if text_chunks:
                    # Create vector store
                    vector_store = FAISS.from_documents(text_chunks, embeddings)
                    
                    # Setup Q&A chain
                    memory = ConversationBufferMemory(
                        memory_key="chat_history",
                        return_messages=True,
                        output_key="answer"
                    )
                    
                    qa_chain = ConversationalRetrievalChain.from_llm(
                        llm=llm,
                        retriever=vector_store.as_retriever(),
                        memory=memory,
                        return_source_documents=True
                    )
                    
                    # Generate analysis
                    full_text = "\n".join([doc.page_content for doc in text_chunks])
                    
                    summary = analyze_text(llm, full_text, "summary")
                    requirements = analyze_text(llm, full_text, "requirements")
                    
                    # Display results
                    st.subheader("Document Overview")
                    st.info(f"Processed {len(set(chunk.metadata.get('source_file', '') for chunk in text_chunks))} files into {len(text_chunks)} text chunks")
                    
                    st.subheader("Executive Summary")
                    st.write(summary)
                    
                    st.subheader("Key Compliance Requirements")
                    st.write(requirements)
                    
                    # Q&A Section
                    st.subheader("Ask Questions")
                    
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.write(message["content"])
                    
                    if prompt := st.chat_input("Ask about the documents"):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        
                        with st.chat_message("user"):
                            st.write(prompt)
                        
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                try:
                                    response = qa_chain.invoke({
                                        "question": prompt,
                                        "chat_history": []
                                    })
                                    answer = response["answer"]
                                    
                                    if response.get("source_documents"):
                                        sources = set(doc.metadata.get('source_file', 'Unknown') 
                                                    for doc in response["source_documents"][:3])
                                        answer += f"\n\nSources: {', '.join(sources)}"
                                    
                                    st.write(answer)
                                    st.session_state.messages.append({"role": "assistant", "content": answer})
                                    
                                except Exception as e:
                                    error_msg = f"Error: {str(e)}"
                                    st.error(error_msg)
                                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Sidebar
    st.sidebar.header("About")
    st.sidebar.info("""
    Analyze multiple tender documents using:
    - OpenAI GPT-OSS-20B
    - FAISS vector search
    - Cross-document Q&A
    """)

if __name__ == "__main__":
    main()