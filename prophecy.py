import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import streamlit_shadcn_ui as ui

st.set_page_config(page_title="Pilotage Magasin", layout="wide", initial_sidebar_state="expanded")

# Font
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

/* Light gray background matching the screenshot */
[data-testid="stAppViewContainer"] {
    background-color: #F3F5F9;
}

[data-testid="stSidebar"] {
    background-color: white;
    border-right: 1px solid #E5E7EB;
}

/* Custom Cards */
.kpi-card {
    background-color: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
    border: 1px solid #E5E7EB;
    height: 100%;
}
.kpi-title {
    color: #4B5563;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.kpi-value {
    color: #111827;
    font-size: 30px;
    font-weight: 600;
}
.kpi-footer {
    margin-top: 12px;
    font-size: 13px;
    color: #9CA3AF;
}
.trend-up {
    color: #10B981;
    font-weight: 600;
    font-size: 12px;
}
.trend-down {
    color: #EF4444;
    font-weight: 600;
    font-size: 12px;
}

/* Custom Top Banner (Total Balance Style) */
.custom-header {
    background: linear-gradient(135deg, #0f5152 0%, #1a7170 100%);
    border-radius: 20px;
    padding: 32px;
    color: white;
    margin-bottom: 32px;
    box-shadow: 0 10px 20px rgba(15, 81, 82, 0.15);
}
.header-title {
    font-size: 15px;
    color: #BBE1E3;
    font-weight: 500;
    margin-bottom: 8px;
}
.header-value {
    font-size: 42px;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.5px;
}
.header-trend {
    color: #34D399;
    font-size: 15px;
    font-weight: 500;
    margin-left: 16px;
    background: rgba(52, 211, 153, 0.1);
    padding: 4px 8px;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# Logo & sidebar
logo_path = 'img/prophecy_logo.png'
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("Prophecy")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
menu = st.sidebar.radio("Menu", [
    "📦 Réassort du Mois",
    "📈 Suivi des Ventes",
    "⚠️ Alertes Ruptures",
    "📂 Historique Commandes"
])

# Data statiques
@st.cache_data
def load_data():
    np.random.seed(42)
    products = ['JBL Charge 5', 'SanDisk Extreme 1TB', 'Sony WH-1000XM4', 'Logitech MX Master 3S', 'Apple AirPods Pro']
    refs = ['OD-JBL-001', 'OD-SD-002', 'OD-SO-003', 'OD-LOG-004', 'OD-APP-005']
    stock_actuel = np.random.randint(0, 30, size=len(products))
    ventes_prevues = np.random.randint(5, 50, size=len(products))
    stock_secu = np.random.randint(2, 10, size=len(products))
    
    df = pd.DataFrame({
        'Produit': [f"{p} ({r})" for p, r in zip(products, refs)],
        'Produit_Name': products,
        'Stock Actuel': stock_actuel,
        'Ventes Prévues': ventes_prevues,
        'Stock Sécurité': stock_secu
    })
    df['Quantité à Commander'] = np.maximum(0, df['Ventes Prévues'] - df['Stock Actuel'] + df['Stock Sécurité'])
    
    def get_urgence(row):
        if row['Stock Actuel'] == 0 or row['Quantité à Commander'] > row['Stock Actuel'] * 2:
            return '🔴 Immédiat'
        elif row['Quantité à Commander'] > 0:
            return '🟠 À prévoir'
        else:
            return '🟢 Stock OK'
            
    df['Niveau d\'Urgence'] = df.apply(get_urgence, axis=1)
    
    dates_past = pd.date_range(end=datetime.now(), periods=30)
    dates_future = pd.date_range(start=datetime.now() + timedelta(days=1), periods=15)
    return df, dates_past, dates_future

df_table, dates_past, dates_future = load_data()

if menu == "📦 Réassort du Mois":
    
    # KPI principal
    valeur_commande = df_table['Quantité à Commander'].sum() * 54.20
    
    st.markdown(f"""
    <div class="custom-header">
        <div class="header-title">Valeur du Réassort (Mois)</div>
        <div style="display: flex; align-items: baseline;">
            <div class="header-value">€ {valeur_commande:,.2f}</div>
            <div class="header-trend">15.8% ↗</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    #  KPI
    c1, c2, c3, c4 = st.columns(4)
    articles_risque = len(df_table[df_table['Niveau d\'Urgence'] == '🔴 Immédiat'])
    
    with c1:
        ui.metric_card(title="🏦 Coût du Réassort", content=f"€ {valeur_commande:,.2f}", description="16.0% ↗ vs. mois dernier", key="card1")
    with c2:
        ui.metric_card(title="⚠️ Articles 'À Risque'", content=str(articles_risque), description="8.2% ↘ vs. hier", key="card2")
    with c3:
        ui.metric_card(title="🛡️ Couverture Stock", content="14 Jours", description="35.2% ↗ de sécurité", key="card3")
    with c4:
        ui.metric_card(title="💸 Ventes Manquées", content="€ 1 240,00", description="12.5% ↘ vs. mois dernier", key="card4")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chart 
    st.markdown("### 📈 Ventes vs Commandes (Simulation)")
    selected_product = st.selectbox("Rechercher un produit :", df_table['Produit_Name'], label_visibility="collapsed")
    
    prod_row = df_table[df_table['Produit_Name'] == selected_product].iloc[0]
    stock_current = prod_row['Stock Actuel']
    
    fig = go.Figure()
    
    y_past = np.random.poisson(lam=stock_current/10 + 2, size=len(dates_past))
    y_future = np.cumsum(np.random.poisson(lam=prod_row['Ventes Prévues']/15, size=len(dates_future)))
    
    # Chart 
    fig.add_trace(go.Bar(
        x=dates_past, 
        y=y_past, 
        name='Ventes Passées', 
        marker_color='#0f5152', 
        opacity=0.9,
        marker_line_width=0
    ))
    
    # Courbe
    fig.add_trace(go.Scatter(
        x=dates_future, 
        y=y_future, 
        mode='lines+markers', 
        name='Prévision Demande IA', 
        line=dict(color='#2ea664', width=3, dash='dot'),
        marker=dict(size=6, color='#2ea664')
    ))

    # Ligne de sécurité 
    fig.add_hline(
        y=stock_current, 
        line_dash="dot", 
        line_color="#9CA3AF", 
        annotation_text=f"Stock Actuel: {stock_current}", 
        annotation_position="top left", 
        annotation_font_color="#4B5563"
    )
    
    fig.update_layout(
        font_family="Inter",
        margin=dict(l=0, r=0, t=20, b=0),
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, linecolor='#E5E7EB', tickfont_color='#9CA3AF'),
        yaxis=dict(showgrid=True, gridcolor='#F3F5F9', linecolor='#E5E7EB', tickfont_color='#9CA3AF')
    )
    
    # Affichage du graphique dans un conteneur style "carte"
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Tableau
    st.markdown("### 📋 Ma Liste de Course Intelligente")
    st.dataframe(
        df_table[['Produit', 'Stock Actuel', 'Ventes Prévues', 'Quantité à Commander', 'Niveau d\'Urgence']],
        use_container_width=True,
        hide_index=True
    )
