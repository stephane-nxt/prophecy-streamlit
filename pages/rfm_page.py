import html
import os
import urllib.parse

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

RFM_PROPHECY_API_URL = os.environ.get("RFM_PROPHECY_API_URL")


def _svg_to_data_uri(svg_markup: str) -> str:
    return "data:image/svg+xml," + urllib.parse.quote(svg_markup, safe="")


def _kpi_theme_primary_hex() -> str:
    try:
        theme = getattr(st.context, "theme", None)
        if theme is not None:
            c = getattr(theme, "primary_color", None) or getattr(theme, "primaryColor", None)
            if c:
                return str(c)
    except Exception:
        pass
    return "#0f5152"


def _kpi_icon_html(svg_markup: str) -> str:
    colored = svg_markup.replace("currentColor", _kpi_theme_primary_hex())
    uri = _svg_to_data_uri(colored)
    return (
        '<span class="metric-card-icon">'
        f'<img src="{uri}" alt="" width="20" height="20" decoding="async" loading="lazy" />'
        "</span>"
    )


_KPI_SVG = {
    "package": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
        '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" points="3.27 6.96 12 12.01 20.73 6.96"/>'
        '<line x1="12" x2="12" y1="22.08" y2="12" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ),
    "cart": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<circle cx="8" cy="21" r="1" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<circle cx="19" cy="21" r="1" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.72a2 2 0 0 0 1.95-1.57l1.65-9.15H5.12"/></svg>'
    ),
    "euro": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M4 10h12"/><path fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 14h9"/>'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M19 6a7.7 7.7 0 0 0-5.2-2A7.5 7.5 0 0 0 6 20h13"/></svg>'
    ),
    "trending_up": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" points="16 7 22 7 22 13"/></svg>'
    ),
}


def _rfm_kpi_card_html(label: str, value: str, subtitle: str, icon_svg: str | None = None) -> str:
    label_esc = html.escape(label)
    value_esc = html.escape(value)
    subtitle_esc = html.escape(subtitle)
    icon_block = ""
    if icon_svg:
        icon_block = _kpi_icon_html(icon_svg)
    return f"""
        <div class="custom-header metric-card">
            <div class="header-title-row">
                {icon_block}
                <p class="header-title">{label_esc}</p>
            </div>
            <p class="header-value">{value_esc}</p>
            <p class="metric-subtitle">{subtitle_esc}</p>
        </div>
        """


def _fmt_grouped_int(n) -> str:
    try:
        return f"{int(float(n)):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


def _fmt_money_ar(n) -> str:
    try:
        amount = f"{float(n):,.2f}".replace(",", " ").replace(".", ",")
        return f"Ar {amount}"
    except (TypeError, ValueError):
        return str(n)


def _fmt_percent(n, decimals: int = 2) -> str:
    try:
        value = f"{float(n):.{decimals}f}".replace(".", ",")
        return f"{value}%"
    except (TypeError, ValueError):
        return str(n)


def _rfm_kpis_section_html(kpis: dict) -> str:
    cards = [
        _rfm_kpi_card_html(
            "Total Clients",
            _fmt_grouped_int(kpis.get("total_clients")),
            "Base de données active",
            icon_svg=_KPI_SVG["package"],
        ),
        _rfm_kpi_card_html(
            "Valeur Moyenne",
            _fmt_money_ar(kpis.get("average_monetary")),
            "Panier moyen cumulé",
            icon_svg=_KPI_SVG["euro"],
        ),
        _rfm_kpi_card_html(
            "Champions",
            _fmt_grouped_int(kpis.get("champions_count")),
            f'{_fmt_percent(kpis.get("champions_pct"))} de la base',
            icon_svg=_KPI_SVG["trending_up"],
        ),
        _rfm_kpi_card_html(
            "Clients B2B",
            _fmt_percent(kpis.get("b2b_pct")),
            f'{_fmt_grouped_int(kpis.get("b2b_count"))} clients pro',
            icon_svg=_KPI_SVG["cart"],
        ),
    ]
    cells = "".join(f'<div class="kpi-grid-item">{c}</div>' for c in cards)
    return f'<div class="kpi-grid kpi-grid--rfm" role="region" aria-label="Indicateurs RFM">{cells}</div>'


def load_segments_rfm():
    response = requests.get(f"{RFM_PROPHECY_API_URL}/segments")
    return response.json()


def load_rfm_dashboard_kpis():
    response = requests.get(f"{RFM_PROPHECY_API_URL}/dashboard/kpis")
    if response.status_code == 200:
        return response.json()
    return {}


def load_interests_list(min_clients=10):
    payload = {"min_clients": min_clients}
    response = requests.get(f"{RFM_PROPHECY_API_URL}/interests", params=payload)
    return response.json()


def rfm():
    data_rfm_kpis = load_rfm_dashboard_kpis()

    st.html(
        """
        <div class="custom-header">
            <div class="header-title">Prophecy</div>
            <div class="header-value" style="font-size: 28px;">
                Segmentation RFM & Profils
                <span class="header-trend">Actualisé</span>
            </div>
        </div>
        """
    )

    if data_rfm_kpis:
        st.html(_rfm_kpis_section_html(data_rfm_kpis))
        st.markdown("<br>", unsafe_allow_html=True)
