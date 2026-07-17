import streamlit as st
import streamlit.components.v1 as components
import time
from supabase import create_client, Client

# 1. Page Configuration
st.set_page_config(page_title="Tync.", page_icon="✨")

# 2. Initialize Supabase Connection
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 3. Initialize Session State for Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. Animated "Bloom Field" Background Component
animated_mesh_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html { margin: 0; padding: 0; overflow: hidden; background-color: #2F5D46; }
        #bg {
            width: 100vw;
            height: 100vh;
            background-color: #2F5D46;
            background-size: 120px 120px, auto, auto, auto, auto;
            background-blend-mode: overlay, normal, normal, normal, normal;
        }
    </style>
</head>
<body>
    <div id="bg"></div>
    <script>
        if (window.frameElement) {
            window.frameElement.style.position = 'fixed';
            window.frameElement.style.top = '0';
            window.frameElement.style.left = '0';
            window.frameElement.style.width = '100vw';
            window.frameElement.style.height = '100vh';
            window.frameElement.style.zIndex = '-1';
            window.frameElement.style.border = 'none';
            window.frameElement.style.pointerEvents = 'none';
        }

        const grain = `url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='0.280'/></svg>")`;

        const blobs = [
            { cx: 66.94, cy: 46.43, stops: "rgba(47, 93, 70, 1) 0%, rgba(47, 93, 70, 0.844) 19.02%, rgba(47, 93, 70, 0.5) 38.05%, rgba(47, 93, 70, 0.156) 57.07%, rgba(47, 93, 70, 0) 76.1%" }, 
            { cx: 34.69, cy: 66.31, stops: "rgba(100, 158, 126, 1) 0%, rgba(100, 158, 126, 0.844) 12.73%, rgba(100, 158, 126, 0.5) 25.45%, rgba(100, 158, 126, 0.156) 38.18%, rgba(100, 158, 126, 0) 50.9%" }, 
            { cx: 48.93, cy: 19.32, stops: "rgba(164, 209, 178, 1) 0%, rgba(164, 209, 178, 0.844) 16.75%, rgba(164, 209, 178, 0.5) 33.5%, rgba(164, 209, 178, 0.156) 50.25%, rgba(164, 209, 178, 0) 67%" }, 
            { cx: 80.23, cy: 87.54, stops: "rgba(238, 246, 227, 1) 0%, rgba(238, 246, 227, 0.844) 10.28%, rgba(238, 246, 227, 0.5) 20.55%, rgba(238, 246, 227, 0.156) 30.83%, rgba(238, 246, 227, 0) 41.1%" }  
        ];

        const seed = 174074637;
        function hash(n) {
            let s = Math.sin(n) * 43758.5453123;
            return s - Math.floor(s);
        }

        blobs.forEach((b, i) => {
            b.p = hash(seed + i * 2) * Math.PI * 2;
            b.p2 = hash(seed + i * 2 + 1) * Math.PI * 2;
        });

        const bgEl = document.getElementById('bg');
        let startT = performance.now();
        const amt = 0.40;
        let rafId;

        function render(now) {
            if (document.hidden) return; 
            const t = (now - startT) / 1000;
            const ph = t * 1.00;

            let gradients = blobs.map(b => {
                const dx = (Math.sin(ph * 0.55 + b.p) - Math.sin(b.p)) * 14 * amt;
                const dy = (Math.sin(ph * 0.43 + b.p2) - Math.sin(b.p2)) * 14 * amt;
                const nx = b.cx + dx;
                const ny = b.cy + dy;
                return `radial-gradient(circle at ${nx}% ${ny}%, ${b.stops})`;
            });

            bgEl.style.backgroundImage = `${grain}, ${gradients.join(', ')}`;
            rafId = requestAnimationFrame(render);
        }
        
        document.addEventListener("visibilitychange", () => {
            if (document.hidden) cancelAnimationFrame(rafId);
            else rafId = requestAnimationFrame(render);
        });

        rafId = requestAnimationFrame(render);
    </script>
</body>
</html>
"""
components.html(animated_mesh_html, height=0, width=0)

# 5. Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lobster&family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&display=swap');

    [data-testid="stAppViewContainer"], .stApp { background: transparent !important; background-color: transparent !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    h1, h2, h3, h4, h5, h6, p, label, div[data-testid="stMarkdownContainer"] > p {
        color: #EEF6E3 !important; 
        font-family: 'Playfair Display', serif !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.4) !important;
    }

    h1 {
        font-family: 'Lobster', cursive !important;
        font-size: 64px !important;
        text-align: center;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5) !important;
    }

    p, label { font-style: italic !important; font-size: 18px !important; }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        border: 1px solid rgba(164, 209, 178, 0.5) !important; 
        border-radius: 10px !important;
        color: #EEF6E3 !important;
        background-color: rgba(47, 93, 70, 0.5) !important; 
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        font-size: 18px !important;
        text-shadow: none !important;
    }
    
    .stTextInput input::placeholder { color: #A4D1B2 !important; opacity: 0.9 !important; }

    div.stButton > button {
        background-color: #649E7E !important; 
        color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 0.6rem 2rem !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        border: 1px solid #EEF6E3 !important;
        font-family: 'Lobster', cursive !important;
        font-size: 24px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        text-shadow: none !important;
    }
    
    div.stButton > button:hover {
        transform: scale(1.05) !important;
        background-color: #A4D1B2 !important; 
        color: #2F5D46 !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5) !important;
    }
    
    div[data-testid="stExpander"] details summary {
        background-color: rgba(47, 93, 70, 0.6) !important; 
        border-radius: 10px !important;
        border: 1px solid rgba(164, 209, 178, 0.4) !important;
    }
    
    div[data-testid="stExpander"] details summary p {
        color: #EEF6E3 !important; 
        font-size: 20px !important;
        text-shadow: none !important;
    }

    div[data-testid="stExpander"] details {
        background-color: rgba(100, 158, 126, 0.4) !important; 
        border-radius: 10px !important;
    }
    
    .stAlert {
        background-color: rgba(47, 93, 70, 0.8) !important;
        border: 1px solid #A4D1B2 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# PAGE 1: LOGIN / SIGNUP SCREEN
# -----------------------------------------
if not st.session_state.logged_in:
    st.title("Tync.")
    st.markdown("### Welcome to the future of team building.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Welcome back!")
        log_user = st.text_input("Username", key="log_user")
        log_pass = st.text_input("Password", type="password", key="log_pass")
        
        if st.button("Login"):
            if log_user and log_pass:
                with st.spinner("Authenticating..."):
                    response = supabase.table("users").select("*").eq("username", log_user).eq("password", log_pass).execute()
                    if len(response.data) > 0:
                        st.session_state.logged_in = True
                        st.session_state.username = log_user
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            else:
                st.warning("Please fill out both fields.")

    with tab2:
        st.subheader("Create an account")
        new_user = st.text_input("Choose a Username", key="new_user")
        new_pass = st.text_input("Choose a Password", type="password", key="new_pass")
        
        if st.button("Sign Up"):
            if new_user and new_pass:
                with st.spinner("Creating account..."):
                    try:
                        supabase.table("users").insert({"username": new_user, "password": new_pass}).execute()
                        st.success("Account created! You can now log in.")
                    except Exception as e:
                        st.error("Username might already be taken. Try another one.")
            else:
                st.warning("Please fill out all fields.")

# -----------------------------------------
# PAGE 2: MAIN MATCHMAKING SCREEN
# -----------------------------------------
else:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Tync.")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown(f"### Hello, {st.session_state.username}! Let's find your team.")
    st.markdown("---") 

    st.subheader("Your Details & Event Setup")
    event_name = st.text_input("Event / Hackathon Name", placeholder="e.g., TKRCET Hackathon 2.0")
    user_skills = st.text_input("Your Current Skills", placeholder="e.g., React.js, Node.js, Python")
    skills_needed = st.text_input("Skills You Are Looking For (One keyword is best)", placeholder="e.g., Python")
    
    if st.button("Update Profile & Find Matches"):
        if not event_name or not skills_needed or not user_skills:
            st.error("Please fill out all fields so we can find you the best match.")
        else:
            with st.spinner("Scanning the database..."):
                supabase.table("users").update({
                    "event_name": event_name,
                    "user_skills": user_skills,
                    "skills_needed": skills_needed
                }).eq("username", st.session_state.username).execute()
                
                matches = supabase.table("users").select("username, user_skills").eq("event_name", event_name).ilike("user_skills", f"%{skills_needed}%").neq("username", st.session_state.username).execute()
                
                if len(matches.data) > 0:
                    st.success(f"Found {len(matches.data)} match(es) for {event_name}!")
                    for idx, match in enumerate(matches.data):
                        st.info(f"**Match #{idx+1}: {match['username']}**\n\nThey have the skills you need: {match['user_skills']}")
                else:
                    st.warning("No perfect matches found yet. Try broadening your skill search, or check back later when more people join the event!")

    st.markdown("---")
    st.markdown("### How to use Tync.")
    
    with st.expander("✨ What does Tync do?"):
        st.markdown("Tync is your personal matchmaking assistant for tech events and hackathons. Instead of wandering around looking for teammates, Tync connects you with people who have the exact skills you're missing, ensuring your team is balanced and ready to win.")

    with st.expander("📝 Step 1: Enter your Event"):
        st.markdown("Type in the name of the hackathon or event you're attending. This ensures we only match you with people who are actually going to the same place you are!")

    with st.expander("🛠️ Step 2: List your Skills"):
        st.markdown("Tell us what you bring to the table. Are you a Python expert? A Figma wizard? The algorithm uses this to make sure you don't overlap too much with your new teammates.")

    with st.expander("🎯 Step 3: Who are you looking for?"):
        st.markdown("List the skills you need to complete your project. Need a frontend developer? Write 'Frontend' or 'React'. Need someone to pitch? Write 'Presentation'.")