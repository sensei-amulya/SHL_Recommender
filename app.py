import streamlit as st
import requests
import json
import os

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium dark styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global Typography Override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0A0D14 0%, #121520 100%) !important;
        color: #E2E8F0 !important;
    }

    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(14, 17, 28, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
    }

    /* Custom Turn Counter Card */
    .turn-counter-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }

    .turn-counter-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 600;
        color: #718096;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }

    .turn-counter-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #00F2FE;
    }

    .turn-counter-bar-bg {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 4px;
        height: 6px;
        width: 100%;
        margin-top: 10px;
        overflow: hidden;
    }

    .turn-counter-bar-fill {
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        height: 100%;
        border-radius: 4px;
        transition: width 0.4s cubic-bezier(0.1, 0.8, 0.25, 1);
    }

    /* Premium Recommendation Cards */
    .recommendation-card {
        border-radius: 16px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }

    .recommendation-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 242, 254, 0.25);
        box-shadow: 0 12px 30px rgba(0, 242, 254, 0.12);
        background: rgba(255, 255, 255, 0.03);
    }

    .recommendation-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 4px;
    }

    .recommendation-link-btn {
        display: inline-block;
        background: linear-gradient(135deg, #1A202C 0%, #2D3748 100%);
        color: #00F2FE !important;
        text-decoration: none !important;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(0, 242, 254, 0.15);
        margin-top: 14px;
        transition: all 0.2s ease;
    }

    .recommendation-link-btn:hover {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        color: #0F111A !important;
        border-color: transparent;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 6px;
        margin-top: 8px;
    }

    .badge-k {
        background: rgba(72, 187, 120, 0.12);
        color: #48BB78;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }

    .badge-p {
        background: rgba(159, 122, 234, 0.12);
        color: #B794F4;
        border: 1px solid rgba(159, 122, 234, 0.3);
    }

    .badge-s {
        background: rgba(49, 130, 206, 0.12);
        color: #63B3ED;
        border: 1px solid rgba(49, 130, 206, 0.3);
    }

    .badge-a {
        background: rgba(221, 107, 32, 0.12);
        color: #F6AD55;
        border: 1px solid rgba(221, 107, 32, 0.3);
    }

    .badge-b {
        background: rgba(229, 62, 62, 0.12);
        color: #FEB2B2;
        border: 1px solid rgba(229, 62, 62, 0.3);
    }

    .badge-c {
        background: rgba(49, 151, 149, 0.12);
        color: #81E6D9;
        border: 1px solid rgba(49, 151, 149, 0.3);
    }

    .badge-d {
        background: rgba(113, 128, 150, 0.12);
        color: #CBD5E0;
        border: 1px solid rgba(113, 128, 150, 0.3);
    }

    .badge-e {
        background: rgba(236, 64, 122, 0.12);
        color: #F48FB1;
        border: 1px solid rgba(236, 64, 122, 0.3);
    }

    .badge-u {
        background: rgba(255, 255, 255, 0.04);
        color: #A0AEC0;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Subheader spacing */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 16px;
        color: #FFFFFF;
        border-bottom: 2px solid rgba(255, 255, 255, 0.03);
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
API_URL = f"{BACKEND_URL}/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "end_of_conversation" not in st.session_state:
    st.session_state.end_of_conversation = False

user_turns = 0
for m in st.session_state.messages:
    if m["role"] == "user":
        user_turns += 1

# Sidebar
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;"><span style="font-size: 2.2rem;">🤖</span><h2 style="margin: 5px 0 0 0; font-weight: 800; background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SHL Advisor</h2></div>', unsafe_allow_html=True)
    st.write("Let our conversational agent match your roles and competencies to the perfect SHL assessments.")
    st.write("")
    
    # Progress visual turn counter
    turn_percentage = min((user_turns / 8) * 100, 100)
    st.markdown(f"""
    <div class="turn-counter-container">
        <div class="turn-counter-title">Conversation Turns</div>
        <div class="turn-counter-value">{user_turns} <span style="font-size: 0.95rem; color: #718096; font-weight: 500;">/ 8 limit</span></div>
        <div class="turn-counter-bar-bg">
            <div class="turn-counter-bar-fill" style="width: {turn_percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("Reset Conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.recommendations = []
        st.session_state.end_of_conversation = False
        st.rerun()
        
    st.write("---")
    st.markdown("""
    ### ⚙️ Quick Tips
    * Mention the **role**, **seniority level**, or specific **competencies** needed.
    * You can request **comparisons** (e.g. *\"compare OPQ and GSA\"*).
    * Refine recommendations by changing or adding requirements mid-chat.
    """)

# Main Content Layout
col_chat, col_recs = st.columns([1.6, 1])

# Badge Helper Function
def render_badges(test_type_str: str) -> str:
    badges = []
    type_mapping = {
        "K": ("Knowledge & Skills (K)", "badge-k"),
        "P": ("Personality & Behavior (P)", "badge-p"),
        "S": ("Simulations (S)", "badge-s"),
        "A": ("Ability & Aptitude (A)", "badge-a"),
        "B": ("Biodata & Situational Judgment (B)", "badge-b"),
        "C": ("Competencies (C)", "badge-c"),
        "D": ("Development & 360 (D)", "badge-d"),
        "E": ("Assessment Exercises (E)", "badge-e"),
        "U": ("Unknown (U)", "badge-u")
    }
    
    parts = [x.strip() for x in test_type_str.split(",") if x.strip()]
    for p in parts:
        if p in type_mapping:
            label, css_class = type_mapping[p]
            badges.append(f'<span class="badge {css_class}">{label}</span>')
        else:
            badges.append(f'<span class="badge badge-u">{p}</span>')
            
    return " ".join(badges)

# Sidebar/Right-column Shortlisted Assessments
with col_recs:
    st.markdown('<div class="section-title">📋 Recommendations Shortlist</div>', unsafe_allow_html=True)
    if st.session_state.recommendations:
        for rec in st.session_state.recommendations:
            badges_html = render_badges(rec.get("test_type", "U"))
            st.markdown(f"""
            <div class="recommendation-card">
                <div class="recommendation-title">{rec['name']}</div>
                <div>{badges_html}</div>
                <a class="recommendation-link-btn" href="{rec['url']}" target="_blank">View Details ↗</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Your recommended shortlist is currently empty. Describe the role requirements to get started!")

# Left-column Chat Feed
with col_chat:
    st.markdown('<div class="section-title">💬 Conversation Partner</div>', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.end_of_conversation:
        st.success("🎉 Conversation concluded. The final assessment recommendation shortlist has been successfully locked in!")
    elif user_turns >= 8:
        st.warning("⚠️ Turn limit reached (8/8). Reset the conversation above to start a new search.")
    else:
        if prompt := st.chat_input("Search or refine profile (e.g. 'Senior Java developer who can review PRs')"):
            # Append User message
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# React to user input and query backend
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not st.session_state.end_of_conversation and user_turns < 8:
    payload_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    payload = {"messages": payload_messages}
    
    with st.spinner("Retrieving matched assessments..."):
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                recommendations = data.get("recommendations", [])
                end_of_conv = data.get("end_of_conversation", False)
                
                # Append Assistant message
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                # Update recommendations shortlist if new recommendations were returned
                if recommendations:
                    st.session_state.recommendations = recommendations
                else:
                    st.session_state.recommendations = recommendations
                    
                st.session_state.end_of_conversation = end_of_conv
                st.rerun()
            else:
                st.error(f"Error from server (Status Code: {response.status_code})")
        except Exception as e:
            st.error(f"Could not connect to FastAPI server. Ensure it is running at {API_URL}. Details: {str(e)}")
