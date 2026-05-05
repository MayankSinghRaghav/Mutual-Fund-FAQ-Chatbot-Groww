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

# Groww Header
st.markdown("""
<div class="groww-header">
    <div class="groww-logo"><div class="logo-circle"></div>Groww</div>
    <div class="nav-link">Stocks</div>
    <div class="nav-link">F&O</div>
    <div class="nav-link" style="color: #00d09c; border-bottom: 2px solid #00d09c;">Mutual Funds</div>
</div>
""", unsafe_allow_html=True)

# Ticker
st.markdown("""
<div class="ticker-container">
    <div class="ticker-item"><div class="ticker-name">NIFTY 50</div><div class="ticker-val">24,052.70 <span class="val-down">▼ 66.60 (0.28%)</span></div></div>
    <div class="ticker-item"><div class="ticker-name">SENSEX</div><div class="ticker-val">77,065.59 <span class="val-down">▼ 203.81 (0.26%)</span></div></div>
    <div class="ticker-item"><div class="ticker-name">BANKNIFTY</div><div class="ticker-val">54,815.95 <span class="val-down">▼ 62.55 (0.11%)</span></div></div>
    <div class="ticker-item"><div class="ticker-name">MIDCPNIFTY</div><div class="ticker-val">13,953.95 <span class="val-up">▲ 23.75 (0.17%)</span></div></div>
</div>
""", unsafe_allow_html=True)

# Dashboard Layout
col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    st.markdown("### Most bought stocks on Groww")
    c1, c2, c3 = st.columns(3)
    
    stocks = [
        {"name": "Titagarh Rail", "price": "₹855.40", "chg": "+11.17%"},
        {"name": "PNB", "price": "₹109.25", "chg": "+0.52%"},
        {"name": "Vedanta", "price": "₹302.30", "chg": "+2.60%"}
    ]
    
    for i, stock in enumerate(stocks):
        with [c1, c2, c3][i]:
            st.markdown(f"""
            <div class="groww-card">
                <div style="font-weight: 700; margin-bottom: 0.5rem;">{stock['name']}</div>
                <div style="font-size: 1.1rem; font-weight: 500;">{stock['price']}</div>
                <div style="color: #00d09c; font-size: 0.85rem; font-weight: 600;">{stock['chg']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Top movers today")
    st.markdown("""
    <div class="groww-card" style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 0.5rem;">
            <span style="color: #7c7e8c; font-size: 0.8rem;">COMPANY</span>
            <span style="color: #7c7e8c; font-size: 0.8rem;">MARKET PRICE</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 1rem 0;">
            <span><b>CG Power & Inds</b></span>
            <span>₹829.45 <span style="color: #00d09c;">(3.38%)</span></span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 1rem 0;">
            <span><b>Vedanta</b></span>
            <span>₹302.30 <span style="color: #00d09c;">(2.60%)</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Your investments")
    st.markdown("""
    <div class="groww-card" style="text-align: center; padding: 3rem 1rem;">
        <img src="https://groww.in/assets/images/no_investment.svg" width="100" style="margin-bottom: 1rem;">
        <div style="color: #7c7e8c;">You haven't invested yet</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Products & Tools")
    tools = [
        {"name": "IPO", "tag": "4 open"},
        {"name": "Bonds", "tag": "12 open"},
        {"name": "ETFs", "tag": ""},
        {"name": "Intraday Screener", "tag": ""}
    ]
    for tool in tools:
        st.markdown(f"""
        <div class="groww-card" style="margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem;">
            <span>{tool['name']}</span>
            <span style="color: #00d09c; font-size: 0.7rem; font-weight: 700;">{tool['tag']}</span>
        </div>
        """, unsafe_allow_html=True)

# FLOATING CHATBOT LOGIC
if "chat_open" not in st.session_state:
    st.session_state.chat_open = True  # Auto pop-up on first load

# CSS for floating window
st.markdown("""
<style>
    .stChatFloating {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        height: 550px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 12px 48px rgba(0,0,0,0.15);
        display: flex;
        flex-direction: column;
        z-index: 10000;
        border: 1px solid #e5e7eb;
    }
    .chat-trigger {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: #00d09c;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,208,156,0.3);
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# Toggle button
if not st.session_state.chat_open:
    if st.button("💬", key="open_chat", help="Open Assistant"):
        st.session_state.chat_open = True
        st.rerun()

# Chat Window
if st.session_state.chat_open:
    with st.container():
        # Fake "Window" header
        st.markdown("""
        <div style="background: #00d09c; color: white; padding: 1rem; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: white; color: #00d09c; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900;">G</div>
                <b>Groww Assistant</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Close button (using Streamlit button for functionality)
        if st.button("✖", key="close_chat"):
            st.session_state.chat_open = False
            st.rerun()

        # Generator Init
        @st.cache_resource
        def get_generator():
            try: return FAQGenerator()
            except Exception as e: return e

        gen = get_generator()
        
        # Chat Box
        chat_container = st.container(height=350)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your Groww Mutual Fund Assistant. How can I help you today?"}]

        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if query := st.chat_input("Ask about funds..."):
            st.session_state.messages.append({"role": "user", "content": query})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(query)
                with st.chat_message("assistant"):
                    if isinstance(gen, Exception):
                        st.error("RAG System not ready. Check API key.")
                    else:
                        with st.spinner("Searching..."):
                            res = gen.generate_answer(query)
                            st.markdown(res["answer"])
                            st.session_state.messages.append({"role": "assistant", "content": res["answer"]})
