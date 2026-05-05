import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent))
try:
    from phase3_llm.generator import FAQGenerator
except Exception as e:
    st.error(f"Failed to import FAQGenerator: {e}")
    st.stop()

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css(Path(__file__).parent / "style.css")

# Custom Header
st.markdown("""
<div class="header-container">
    <div class="logo-text">HDFC<span class="logo-accent">AI</span></div>
    <div class="nav-links">
        <a href="#" class="nav-item active">Dashboard</a>
        <a href="#" class="nav-item">Funds</a>
        <a href="#" class="nav-item">Portfolio</a>
        <a href="#" class="nav-item">Support</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### Portfolio Overview")
    
    # Summary Metrics
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""
        <div class="metric-card">
            <div class="card-title">Current Value</div>
            <div class="card-value">₹12,45,200</div>
            <div style="color: #10b981; font-size: 0.8rem; font-weight: 600;">+14.2% Overall</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="metric-card">
            <div class="card-title">Annualized Returns</div>
            <div class="card-value">18.5%</div>
            <div style="color: #10b981; font-size: 0.8rem; font-weight: 600;">Above Benchmark</div>
        </div>
        """, unsafe_allow_html=True)

    # Fund List
    st.markdown("#### Your Active Funds")
    funds = [
        {"name": "HDFC Mid-Cap Opportunities", "value": "₹4,20,000", "return": "+22.4%"},
        {"name": "HDFC Large Cap Fund", "value": "₹5,10,000", "return": "+12.1%"},
        {"name": "HDFC Focused Fund", "value": "₹3,15,200", "return": "+8.5%"}
    ]
    
    for fund in funds:
        st.markdown(f"""
        <div class="metric-card" style="padding: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: 600; font-size: 0.9rem;">{fund['name']}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">{fund['value']}</div>
            </div>
            <div style="color: #10b981; font-weight: 700;">{fund['return']}</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # Chat Interface inside a container
    st.markdown("""
    <div class="chat-header">
        <div class="bot-icon">H</div>
        <div>
            <div style="font-weight: 700; font-size: 1rem;">HDFC Smart Assistant</div>
            <div style="font-size: 0.75rem; opacity: 0.8;">Online | Fact-checked RAG</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize messages if not present
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your HDFC Mutual Fund Assistant. Ask me anything about HDFC schemes, expense ratios, or fund performance."}
        ]

    # API Key Management (moved to sidebar)
    api_key = os.getenv("GEMINI_API_KEY")
    with st.sidebar:
        st.header("Security Settings")
        if not api_key:
            api_key_input = st.text_input("Gemini API Key:", type="password")
            if api_key_input:
                os.environ["GEMINI_API_KEY"] = api_key_input
                st.rerun()
        else:
            st.success("API Key active")
            if st.button("Reset Session"):
                st.session_state.messages = []
                st.rerun()

    if not os.getenv("GEMINI_API_KEY"):
        st.warning("Please configure your API key in the sidebar.")
        st.stop()

    # Generator Init
    @st.cache_resource
    def get_generator():
        try: return FAQGenerator()
        except Exception as e: return e

    gen = get_generator()
    if isinstance(gen, Exception):
        st.error(f"Initialization Error: {gen}")
        st.stop()

    # Chat Scroll Area
    chat_box = st.container(height=500, border=False)
    
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input
    if query := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": query})
        with chat_box:
            with st.chat_message("user"):
                st.markdown(query)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data..."):
                    res = gen.generate_answer(query)
                    answer = res["answer"]
                    st.markdown(answer)
        
        st.session_state.messages.append({"role": "assistant", "content": answer})
