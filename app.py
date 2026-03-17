import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

def get_authenticator():
    with open('config.yaml', 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

def dashboard(auth):
    with st.container():
        st.title(f"Welcome {st.session_state.get("username")}")
        

auth = get_authenticator()

st.set_page_config(page_title="Prophecy", page_icon="🔮", layout="centered")

try:
    auth.login()
except Exception as e:
    st.error(e)

if st.session_state.get('authentication_status'):
    dashboard(auth)
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

