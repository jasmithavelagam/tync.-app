import streamlit as st
import streamlit.components.v1 as components
import time
import requests
from supabase import create_client, Client
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="Tync.", page_icon="✨")

# 2. Initialize Connections
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_resource
def init_groq():
    # This will use your secret key from Streamlit Cloud
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

supabase = init_connection()
groq_client = init_groq()

# 3. Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. CUSTOM CSS (Retro Poster Theme + Burgundy Text + BaseWeb Overrides)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lobster&family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&family=Space+Mono:wght@400;700&display=swap');

    /* Page background */
    .stApp {
        background-color: #EDE8DA !important;
        background-image: radial-gradient(rgba(0,0,0,0.03) 1px, transparent 1px), radial-gradient(rgba(0,0,0,0.02) 1px, transparent 1px) !important;
        background-size: 3px 3px, 5px 5px !important;
    }

    /* Hide default Streamlit header */
    [data-testid="stHeader"] { background-color: transparent !important; }

    /* Typography: Burgundy & Old Fonts */
    h1, h2, h3, p, label, .stMarkdown, .stInfo, .stSuccess, .stError, .stWarning { 
        color: #800020 !important; 
        font-family: 'Playfair Display', serif !important;
    }
    h1 { 
        font-family: 'Lobster', cursive !important; 
        font-size: 72px !important; 
        text-align: center; 
        text-shadow: none !important;
    }

    /* HARDENED INPUT STYLE: Fixes the dark grey boxes shown in your screenshots */
    div[data-baseweb="input"] {
        background-color: transparent !important;
        border: 2px solid #800020 !important;
        border-radius: 0px !important;
    }
    div[data-baseweb="base-input"] {
        background-color: transparent !important;
    }
    .stTextInput input, .stTextArea textarea, .stNumberInput input { 
        background-color: #EDE8DA !important; 
        color: #800020 !important; 
        font-family: 'Space Mono', monospace !important;
        -webkit-text-fill-color: #800020 !important; /* Forces text color in WebKit browsers */
    }

    /* Focus state for inputs */
    div[data-baseweb="input"]:focus-within {
        border-color: #800020 !important;
        box-shadow: 0 0 5px rgba(128, 0, 32, 0.5) !important;
    }

    /* Buttons: Burgundy background, Cream text */
    div.stButton > button { 
        background-color: #800020 !important; 
        border-radius: 0px !important; 
        border: none !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        transition: transform 0.2s ease !important;
    }
    div.stButton > button p {
        color: #EDE8DA !important; 
        font-family: 'Space Mono', monospace !important;
        font-size: 16px !important;
    }
    div.stButton > button:hover { 
        transform: scale(1.02) !important;
        background-color: #5a0016 !important; 
    }

    /* Straight top border */
    .zigzag-top {
        height: 4px; width: 100%;
        background-color: #800020;
        margin-bottom: 25px;
    }

    /* Alerts and Expanders */
    .stAlert { background-color: #EDE8DA !important; border: 1px solid #800020 !important; border-radius: 0px !important; }
    div[data-testid="stExpander"] details { background-color: #EDE8DA !important; border: 1px solid #800020 !important; border-radius: 0px !important; }
    div[data-testid="stExpander"] details summary p { color: #800020 !important; font-weight: 600 !important; }
    div[data-testid="stExpander"] details summary svg { fill: #800020 !important; }

    hr { border-color: #800020 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Render top border
st.markdown('<div class="zigzag-top"></div>', unsafe_allow_html=True)

# -----------------------------------------
# MAIN LOGIC
# -----------------------------------------
if not st.session_state.logged_in:
    st.title("Tync.")
    st.markdown("### Welcome to the future of team building.")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        log_user = st.text_input("Username", key="log_user")
        log_pass = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            if log_user and log_pass:
                response = supabase.table("users").select("*").eq("username", log_user).eq("password", log_pass).execute()
                if len(response.data) > 0:
                    st.session_state.logged_in = True
                    st.session_state.username = log_user
                    st.rerun()
                else: st.error("Invalid username or password.")
            else: st.warning("Please fill out both fields.")
    with tab2:
        st.subheader("Create an account")
        new_user = st.text_input("Choose a Username", key="new_user")
        new_pass = st.text_input("Choose a Password", type="password", key="new_pass")
        if st.button("Sign Up"):
            if new_user and new_pass:
                try:
                    supabase.table("users").insert({"username": new_user, "password": new_pass}).execute()
                    st.success("Account created!")
                except: st.error("Username taken.")
            else: st.warning("Please fill all fields.")
else:
    col1, col2 = st.columns([4, 1])
    with col1: st.title("Tync.")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    event_name = st.text_input("Event Name")
    user_skills = st.text_input("Your Skills")
    skills_needed = st.text_input("Skills Needed")

    if st.button("Update Profile & Find Matches"):
        if not event_name or not skills_needed or not user_skills:
            st.error("Please fill all fields.")
        else:
            with st.spinner("Scanning database..."):
                supabase.table("users").update({"event_name": event_name, "user_skills": user_skills, "skills_needed": skills_needed}).eq("username", st.session_state.username).execute()
                matches = supabase.table("users").select("username, user_skills").eq("event_name", event_name).ilike("user_skills", f"%{skills_needed}%").neq("username", st.session_state.username).execute()

                # --- AI INTEGRATION SAFETY BLOCK ---
                try:
                    prompt = f"I am at {event_name}. I have {user_skills} and need {skills_needed}. Give me a 1-sentence tip on how to pitch to potential teammates."
                    ai_res = groq_client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
                    st.success(f"Found {len(matches.data)} match(es)!")
                    st.info(f"**AI Tip:** {ai_res.choices[0].message.content}")
                except Exception as e:
                    st.error("Matches found, but AI Tip failed. Check API Key in settings.")
                    st.write(f"Matches found: {len(matches.data)}")

                for idx, match in enumerate(matches.data):
                    st.info(f"**Match #{idx+1}: {match['username']}** - Skills: {match['user_skills']}")

    st.markdown("---")
    with st.expander("✨ What does Tync do?"): st.markdown("Matchmaking assistant for hackathons.")
    with st.expander("📝 Step 1: Enter your Event"):
        st.markdown("...")

    with st.expander("🛠️ Step 2: List your Skills"):
        st.markdown("...")

    with st.expander("🎯 Step 3: Who are you looking for?"):
        st.markdown("...")