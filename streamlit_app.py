import streamlit as st
import requests
import google.generativeai as genai
import urllib.parse

# --- CONFIGURE META & GOOGLE GEMINI --- 
META_APP_ID = "your_meta_app_id"
META_APP_SECRET = "your_meta_app_secret"
REDIRECT_URI = "https://your-streamlit-app-url.com"  # Update with your actual Streamlit URL

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Securely store API Key in secrets

# --- META OAUTH LOGIN URL ---
auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={META_APP_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope=pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish"

# --- STREAMLIT UI ---
st.title("Ever AI - Social Media Auto-Poster")
st.write("Generate AI content and post it to Facebook & Instagram.")

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

# --- POST TO FACEBOOK ---
if "access_token" in st.session_state and "generated_content" in st.session_state:
    if st.button("📢 Post to Facebook"):
        pages_url = f"https://graph.facebook.com/me/accounts?access_token={st.session_state['access_token']}"
        pages_response = requests.get(pages_url).json()

        if "data" in pages_response:
            pages = {page['name']: page['id'] for page in pages_response['data']}
            selected_page = st.selectbox("Select a Facebook Page:", list(pages.keys()))

            page_id = pages[selected_page]
            post_url = f"https://graph.facebook.com/{page_id}/feed"
            post_payload = {"message": st.session_state["generated_content"], "access_token": st.session_state["access_token"]}

            post_response = requests.post(post_url, data=post_payload)
            if post_response.status_code == 200:
                st.success("✅ Successfully posted to Facebook!")
            else:
                st.error(f"❌ Error: {post_response.text}")

# --- POST TO INSTAGRAM ---
if "access_token" in st.session_state and "generated_content" in st.session_state:
    if st.button("📷 Post to Instagram"):
        insta_url = f"https://graph.facebook.com/v18.0/me/media"
        insta_payload = {
            "caption": st.session_state["generated_content"],
            "access_token": st.session_state["access_token"]
        }

        insta_response = requests.post(insta_url, data=insta_payload)
        if insta_response.status_code == 200:
            st.success("✅ Successfully posted to Instagram!")
        else:
            st.error(f"❌ Error: {insta_response.text}")

