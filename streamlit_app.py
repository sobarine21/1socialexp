import streamlit as st
import requests
import google.generativeai as genai
import urllib.parse

# --- CONFIGURE THREADS & GOOGLE GEMINI --- 
THREADS_APP_ID = "your_threads_app_id"  # Replace with your Threads App ID
THREADS_APP_SECRET = "your_threads_app_secret"  # Replace with your Threads App Secret
REDIRECT_URI = "https://your-streamlit-app-url.com"  # Update with your actual Streamlit URL

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Securely store API Key in secrets

# --- THREADS OAUTH LOGIN URL ---
auth_url = f"https://www.threads.com/oauth/authorize?client_id={THREADS_APP_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope=read_write"  # Assuming 'read_write' is the required scope

# --- STREAMLIT UI ---
st.title("Ever AI - Social Media Auto-Poster")
st.write("Generate AI content and post it to Threads.")

# --- HANDLE THREADS LOGIN ---
if "access_token" not in st.session_state:
    st.markdown(f"[🔑 Login with Threads]({auth_url})")
else:
    st.success("✅ Logged into Threads!")

# --- HANDLE OAUTH REDIRECT ---
if "code" in st.query_params:
    auth_code = st.query_params["code"]
    token_url = f"https://api.threads.com/oauth/access_token?client_id={THREADS_APP_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&client_secret={THREADS_APP_SECRET}&code={auth_code}"
    
    response = requests.get(token_url).json()
    if "access_token" in response:
        st.session_state["access_token"] = response["access_token"]
        st.success("✅ Threads Authentication Successful!")
    else:
        st.error("❌ Failed to authenticate with Threads.")

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

# --- POST TO THREADS ---
if "access_token" in st.session_state and "generated_content" in st.session_state:
    if st.button("📢 Post to Threads"):
        post_url = "https://api.threads.com/v1/posts"  # Adjusted for Threads API endpoint
        post_payload = {
            "message": st.session_state["generated_content"],
            "access_token": st.session_state["access_token"]
        }

        post_response = requests.post(post_url, json=post_payload)
        if post_response.status_code == 200:
            st.success("✅ Successfully posted to Threads!")
        else:
            st.error(f"❌ Error: {post_response.text}")
