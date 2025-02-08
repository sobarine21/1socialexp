import streamlit as st
import requests
import google.generativeai as genai
import urllib.parse

# --- CONFIGURE META & GOOGLE GEMINI --- 
META_APP_ID = "your_meta_app_id"  # Replace with your actual Meta App ID
META_APP_SECRET = "your_meta_app_secret"  # Replace with your actual Meta App Secret
REDIRECT_URI = "https://your-streamlit-app-url.com"  # Replace with your actual Streamlit URL

# Initialize Google Gemini API for content generation
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Securely store API Key in secrets

# --- META OAUTH LOGIN URL ---
auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={META_APP_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope=public_profile,pages_manage_posts,pages_read_engagement"

# --- STREAMLIT UI ---
st.title("Ever AI - Threads Auto-Poster")
st.write("Generate AI content and post it to Threads.")

# --- HANDLE META LOGIN ---
if "access_token" not in st.session_state:
    st.markdown(f"[🔑 Login with Meta]({auth_url})")
else:
    st.success("✅ Logged into Meta!")

# --- HANDLE OAUTH REDIRECT ---
if "code" in st.query_params:
    auth_code = st.query_params["code"]
    token_url = f"https://graph.facebook.com/v18.0/oauth/access_token?client_id={META_APP_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&client_secret={META_APP_SECRET}&code={auth_code}"
    
    response = requests.get(token_url).json()
    if "access_token" in response:
        st.session_state["access_token"] = response["access_token"]
        st.success("✅ Meta Authentication Successful!")
    else:
        st.error("❌ Failed to authenticate with Meta.")

# --- GENERATE AI CONTENT ---
prompt = st.text_input("Enter a prompt for AI content:", "Best alternatives to JavaScript?")
if st.button("Generate AI Content"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.session_state["generated_content"] = response.text
        st.write("### 📝 AI-Generated Content:")
        st.write(response.text)
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- POST TO THREADS (Meta's Threads API) ---
if "access_token" in st.session_state and "generated_content" in st.session_state:
    if st.button("📢 Post to Threads"):
        # The Threads API is currently managed through Meta's Graph API
        threads_url = f"https://graph.facebook.com/v18.0/me/media"
        threads_payload = {
            "caption": st.session_state["generated_content"],  # AI-generated content as caption
            "access_token": st.session_state["access_token"]  # The user’s access token
        }

        threads_response = requests.post(threads_url, data=threads_payload)
        
        if threads_response.status_code == 200:
            st.success("✅ Successfully posted to Threads!")
        else:
            st.error(f"❌ Error: {threads_response.text}")

