import streamlit as st
import PyPDF2
import io
import re
import os
from datetime import datetime
import json
import base64
from typing import List, Dict, Any

# Set page config
st.set_page_config(
    page_title="Tender Digest AI - Global Tender Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .analysis-result {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
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
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Tender Digest AI</h1>
    <p>Global Tender Analysis & Intelligence System - Fast & Free Version</p>
</div>
""", unsafe_allow_html=True)

class FastTenderAnalyzer:
    """Lightweight tender analysis using rule-based methods for fast deployment"""
    
    def __init__(self):
        self.tender_keywords = {
            'construction': ['construction', 'building', 'infrastructure', 'civil work', 'concrete', 'steel', 'contractor'],
            'it_software': ['software', 'IT', 'computer', 'system', 'application', 'development', 'programming'],
            'medical': ['medical', 'healthcare', 'hospital', 'pharmaceutical', 'equipment', 'surgical'],
            'transportation': ['transport', 'vehicle', 'logistics', 'shipping', 'delivery', 'freight'],
            'education': ['education', 'school', 'university', 'training', 'academic', 'learning'],
            'security': ['security', 'surveillance', 'guard', 'safety', 'protection', 'monitoring'],
            'maintenance': ['maintenance', 'repair', 'service', 'upkeep', 'cleaning', 'facility'],
            'supply': ['supply', 'procurement', 'purchase', 'goods', 'materials', 'equipment']
        }
        
        self.risk_indicators = [
            'urgent', 'immediate', 'emergency', 'single source', 'limited time',
            'restricted', 'pre-qualified', 'invitation only', 'complex technical'
        ]
        
        self.value_patterns = [
            r'₹\s*[\d,]+(?:\.\d+)?(?:\s*(?:crore|lakh|thousand))?',
            r'\$\s*[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand))?',
            r'EUR\s*[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand))?',
            r'value:\s*[\d,]+', r'amount:\s*[\d,]+', r'budget:\s*[\d,]+'
        ]

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
        st.session_state.analyzer = FastTenderAnalyzer()
    
    # Sidebar
    st.sidebar.markdown("### 📤 Upload Documents")
    st.sidebar.markdown("Upload up to 10 PDF tender documents for analysis")
    
    # File uploader
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
    
    # Main content
    if uploaded_files:
        st.markdown(f"### 📄 Documents Uploaded: {len(uploaded_files)}")
        
        # Display uploaded files
        cols = st.columns(min(len(uploaded_files), 3))
        for i, file in enumerate(uploaded_files):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>📄 {file.name}</h4>
                    <p>Size: {file.size / 1024:.1f} KB</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Analysis button
        if st.button("🚀 Analyze Tender Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_results = []
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Analyzing {file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Extract text
                text = st.session_state.analyzer.extract_text_from_pdf(file)
                
                if text:
                    # Perform analysis
                    analysis_result = {
                        'filename': file.name,
                        'category': st.session_state.analyzer.analyze_tender_category(text),
                        'key_info': st.session_state.analyzer.extract_key_information(text),
                        'competition': st.session_state.analyzer.assess_competition_level(text),
                        'risk': st.session_state.analyzer.calculate_risk_score(text),
                        'text_length': len(text),
                        'word_count': len(text.split())
                    }
                    
                    if include_recommendations:
                        analysis_result['recommendations'] = st.session_state.analyzer.generate_recommendations(analysis_result)
                    
                    all_results.append(analysis_result)
            
            status_text.text("Analysis complete!")
            progress_bar.progress(1.0)
            
            # Display results
            st.markdown("## 📊 Analysis Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>Documents Analyzed</p>
                </div>
                """.format(len(all_results)), unsafe_allow_html=True)
            
            with col2:
                categories = [r['category']['primary_category'] for r in all_results]
                unique_cats = len(set(categories))
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>Unique Categories</p>
                </div>
                """.format(unique_cats), unsafe_allow_html=True)
            
            with col3:
                high_risk = sum(1 for r in all_results if r['risk']['level'] == 'High')
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>High Risk Tenders</p>
                </div>
                """.format(high_risk), unsafe_allow_html=True)
            
            with col4:
                high_competition = sum(1 for r in all_results if r['competition']['level'] == 'High')
                st.markdown("""
                <div class="metric-card">
                    <h3>{}</h3>
                    <p>High Competition</p>
                </div>
                """.format(high_competition), unsafe_allow_html=True)
            
            # Individual results
            for i, result in enumerate(all_results):
                st.markdown(f"### 📄 {result['filename']}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="analysis-result">
                        <h4>🏷️ Category: {result['category']['primary_category']}</h4>
                        <p><strong>Confidence:</strong> {result['category']['confidence']:.1f}%</p>
                        
                        <h4>📋 Key Information:</h4>
                        <ul>
                            <li><strong>Tender Number:</strong> {result['key_info']['tender_number'] or 'Not found'}</li>
                            <li><strong>Organization:</strong> {result['key_info']['organization'] or 'Not found'}</li>
                            <li><strong>Estimated Value:</strong> {result['key_info']['estimated_value'] or 'Not found'}</li>
                            <li><strong>Deadline:</strong> {result['key_info']['deadline'] or 'Not found'}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="feature-card">
                        <h4>🎯 Competition Level</h4>
                        <p><strong>{result['competition']['level']}</strong></p>
                        <p>Confidence: {result['competition']['confidence']:.1f}%</p>
                        
                        <h4>⚠️ Risk Score</h4>
                        <p><strong>{result['risk']['level']}</strong></p>
                        <p>Score: {result['risk']['score']:.1f}%</p>
                        
                        <h4>📊 Document Stats</h4>
                        <p>Words: {result['word_count']:,}</p>
                        <p>Characters: {result['text_length']:,}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Recommendations
                if include_recommendations and 'recommendations' in result:
                    st.markdown("#### 💡 Recommendations:")
                    for j, rec in enumerate(result['recommendations'], 1):
                        st.markdown(f"{j}. {rec}")
                
                st.markdown("---")
            
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
        # Welcome screen
        st.markdown("""
        <div class="upload-section">
            <h3>🚀 Welcome to Tender Digest AI</h3>
            <p>This is the fast, deployment-optimized version designed for free hosting platforms.</p>
            <p>Upload your tender documents using the sidebar to get started!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🏷️ Smart Categorization</h4>
                <p>Automatically categorize tenders by industry and type using advanced keyword analysis.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>📊 Risk Assessment</h4>
                <p>Evaluate tender complexity and competition levels to make informed decisions.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>💡 Smart Recommendations</h4>
                <p>Get actionable insights and recommendations for each tender opportunity.</p>
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