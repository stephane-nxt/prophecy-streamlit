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

def load_categories():
    response = requests.get(f'{API_URL}/categories')
    return response.json()['data']

def make_reassort(category_id, urgency_selected, growth_selected, quantity_selected, limit_selected, offset_selected):
    payload = {
        'category_id': category_id,
        'alert': urgency_selected,
        'cycle': growth_selected,
        'min_qty': quantity_selected,
        'limit': limit_selected,
        'offset': offset_selected
    }
    response = requests.get(f'{API_URL}/reassort', params=payload)
    result = []
    if response.status_code == 200:
        data = response.json()
        if len(data['data']) > 0:
            for item in data['data']:
                result.append({
                    'Article': item['product_name'],
                    'Ventes prévues en 30 jours': item['ventes_prevues_30j'],
                    'Quantité en stock': item['qty_available'],
                    'Quantité à commander': item['qty_to_order'],
                    'Etat de l\'article': item['cycle_status'],
                    'Etat du stock': item['alert'],
                    'Date idéale pour commander': item['order_by_date']
                })
            return result
        else:
            return result
    else:
        return result

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
    data_categories = load_categories()
    logo_path = 'img/prophecy_logo.png'
    
    with st.sidebar:
        if os.path.exists(logo_path):
            st.image(logo_path, width='content')
        else:
            st.title("Prophecy")
        st.markdown("<br>", unsafe_allow_html=True)
        auth.logout()

    st.title(f"Bienvenue {st.session_state.get("username")},")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col_1_1, col_1_2, col_1_3 = st.columns(3)
        col_2_1, col_2_2, col_2_3 = st.columns(3)
        with col_1_1:
            st.metric(label="Total des produits", value=data_stats['total_products'], border=True)
        with col_1_2:
            st.metric(label="Produits à commander", value=data_stats['products_to_order'], border=True)
        with col_1_3:
            st.metric(label="Coût estimé du réassort", value=data_stats['estimated_total_cost'], border=True)
        with col_2_1:
            st.metric(label="Rupture imminente", value=data_stats['rupture_imminente'], help="Le stock sera vide avant la livraison", border=True)
        with col_2_2:
            st.metric(label="Forte demande", value=data_stats['forte_demande'], border=True)
        with col_2_3:
            st.metric(label="Produits obsolètes", value=data_stats['obsolete'], border=True)
        st.metric(label="Couverture stock", value=data_stats['avg_coverage_days'], help="Combien de jours le stock actuel peut tenir avant rupture", border=True, format="%.2f jours")
        
    st.divider()

    st.title("Faire un Réassort")
    with st.container(border=True):
        category_selected = st.selectbox("Select a category", [category['category'] for category in data_categories], index=None)
        col_1_1, col_1_2, col_1_3 = st.columns(3)
        col_2_1, col_2_2 = st.columns(2)
        with col_1_1:
            # Rupture imminente, Forte demande, À commander, Stable, Stock OK, Ne pas recommander
            urgency_selected = st.selectbox("Select an urgency", ["Rupture imminente", "Forte demande", "À commander", "Stable", "Stock OK", "Ne pas recommander"], index=None)
        with col_1_2:
            #Croissance, Maturité, Déclin, Obsolescence, Inactif
            growth_selected = st.selectbox("Select a growth", ["Croissance", "Maturité", "Déclin", "Obsolescence", "Inactif"], index=None)
        with col_1_3:
            #Quantité à commander minimum
            quantity_selected = st.number_input("Minimum quantity to order", min_value=1, value=1, step=1)
        with col_2_1:
            limit_selected = st.number_input("Limit selected", min_value=1, value=100, step=50)
        with col_2_2:
            offset_selected = st.number_input("Offset selected", min_value=0, value=0, step=50)
        is_clicked = st.button("Make a reassort", type="primary")
        if is_clicked:
            category_id = None
            if category_selected is not None:
                category_id = [category['category_id'] for category in data_categories if category['category'] == category_selected][0]
            data_reassort = make_reassort(category_id, urgency_selected, growth_selected, quantity_selected, limit_selected, offset_selected)
            if len(data_reassort) > 0:
                st.dataframe(data_reassort)
            else:
                st.error("No reassort data found")
            

auth = get_authenticator()

st.set_page_config(page_title="Prophecy", page_icon='img/favicon.png', layout="wide")

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

