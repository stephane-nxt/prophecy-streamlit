import io
import streamlit as st
import yaml
import boto3
import pandas as pd
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import os
import plotly.express as px
import requests

API_URL = os.environ.get('PROPHECY_API_URL')

def get_authenticator():
    with open('config.yaml', 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

def load_stats():
    response = requests.get(f'{API_URL}/stats')
    return response.json()

@st.cache_data
def load_data():
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name = os.environ.get('AWS_REGION'),
    )

    response = s3.get_object(Bucket=os.environ.get('AWS_BUCKET_NAME'), Key="demoday-dataset/sales_history.parquet")

    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        body = response.get('Body')
        buffer = io.BytesIO(body.read())
        data = pd.read_parquet(buffer)
        data['is_sold'] = data['qty_sold'].apply(lambda x: "Sold" if x > 0 else "Not Sold")
        return data
    else:
        return None

def top_data(data, column_name, top_n=None):
    value_counts = data[column_name].value_counts(normalize=False)
    result = pd.DataFrame({
        column_name: value_counts.index,
        "count": value_counts.values
    })
    if top_n is not None:
        return result.head(top_n)
    else:
        return result

def dashboard(auth):
    # data = load_data()
    data_stats = load_stats()
    logo_path = 'img/prophecy_logo.png'
    with st.sidebar:
        if os.path.exists(logo_path):
            st.image(logo_path, width='content')
        else:
            st.title("Prophecy")
        st.markdown("<br>", unsafe_allow_html=True)
        auth.logout()
    
    with st.container():
        st.title(f"Bienvenue {st.session_state.get("username")},")
        col_1_1, col_1_2, col_1_3 = st.columns(3)
        col_2_1, col_2_2, col_2_3 = st.columns(3)
        with col_1_1:
            st.metric(label="Total des produits", value=data_stats['total_products'])
        with col_1_2:
            st.metric(label="Produits à commander", value=data_stats['products_to_order'])
        with col_1_3:
            st.metric(label="Coût estimé du réassort", value=data_stats['estimated_total_cost'])
        with col_2_1:
            st.metric(label="Rupture imminente", value=data_stats['rupture_imminente'], help="Le stock sera vide avant la livraison")
        with col_2_2:
            st.metric(label="Forte demande", value=data_stats['forte_demande'])
        with col_2_3:
            st.metric(label="Produits obsolètes", value=data_stats['obsolete'])
        st.metric(label="Couverture stock", value=data_stats['avg_coverage_days'])
        
auth = get_authenticator()
st.set_page_config(page_title="Prophecy", page_icon="🔮", layout="wide")

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

