import io
import streamlit as st
import yaml
import boto3
import pandas as pd
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import os
import plotly.express as px

def get_authenticator():
    with open('config.yaml', 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

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
    data = load_data()
    
    with st.container():
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.title(f"Welcome {st.session_state.get("username")}")
        with header_col2:
            auth.logout()
        if data is not None:
            top_product = top_data(data, "product_name")
            top_category = top_data(data, "category")
            top_sold = top_data(data, "is_sold")
            col1, col2, col3 = st.columns(3)
            with col1:
                fig_sold = px.pie(top_sold, values="count", names="is_sold", title="Sold vs Not Sold")
                st.plotly_chart(fig_sold, width="stretch")
            with col2:
                fig_category = px.bar(top_category, x="category", y="count", title="Top Categories")
                st.plotly_chart(fig_category, width="stretch")
            with col3:
                fig_product = px.bar(top_product, x="product_name", y="count", title="Top Products")
                st.plotly_chart(fig_product, width="stretch")
        else:
            st.error("No data found")


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

