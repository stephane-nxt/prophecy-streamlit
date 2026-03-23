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
    "users": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    ),
    "money": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<rect x="2" y="6" width="20" height="12" rx="2" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M6 10h.01M18 14h.01"/></svg>'
    ),
    "badge_trend": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" d="M12 3l2.4 2.2 3.2-.2 1.4 2.9 2.8 1.6-.6 3.1 1.4 2.8-2.4 2.2-.2 3.2-2.9 1.4-1.6 2.8-3.1-.6-2.8 1.4-2.2-2.4-3.2-.2-1.4-2.9-2.8-1.6.6-3.1-1.4-2.8 2.4-2.2.2-3.2 2.9-1.4 1.6-2.8z"/>'
        '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" points="8 14 11 11 13 13 16 10"/>'
        '<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" points="14.5 10 16 10 16 11.5"/></svg>'
    ),
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


def _rfm_kpi_card_html(
    label: str,
    value: str,
    subtitle: str,
    icon_svg: str | None = None,
    icon_emoji: str | None = None,
) -> str:
    label_esc = html.escape(label)
    value_esc = html.escape(value)
    subtitle_esc = html.escape(subtitle)
    icon_block = ""
    if icon_emoji:
        icon_block = f'<span class="metric-card-icon" aria-hidden="true">{html.escape(icon_emoji)}</span>'
    elif icon_svg:
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
            icon_emoji="👥",
        ),
        _rfm_kpi_card_html(
            "Valeur Moyenne",
            _fmt_money_ar(kpis.get("average_monetary")),
            "Panier moyen cumulé",
            icon_emoji="💰",
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
    data_segments = load_segments_rfm()
    data_rfm_kpis = load_rfm_dashboard_kpis()
    segment_palette = ["#025864", "#00d47e", "#f4c095", "#ee2e31"]

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

    st.markdown("### Performance des segments clients")

    by_segment = data_segments.get("by_segment", []) if isinstance(data_segments, dict) else []
    by_segment_ca = data_segments.get("by_segment_ca", []) if isinstance(data_segments, dict) else []
    if by_segment:
        seg_df = pd.DataFrame(by_segment)
        seg_df["count"] = pd.to_numeric(seg_df["count"], errors="coerce").fillna(0)
        seg_df["part"] = (seg_df["count"] / max(seg_df["count"].sum(), 1)) * 100
        seg_df = seg_df.sort_values("count", ascending=False)

        ca_df = pd.DataFrame(by_segment_ca) if by_segment_ca else pd.DataFrame(columns=["segment", "ca"])
        if not ca_df.empty:
            ca_df["ca"] = pd.to_numeric(ca_df["ca"], errors="coerce").fillna(0)
            ca_df = ca_df.sort_values("ca", ascending=False)

        col1, col2 = st.columns(2, gap="small")

        with col1:
            with st.container(border=True):
                st.markdown("### 💰 CA par segment")
                if not ca_df.empty:
                    fig_bar_ca = px.bar(
                        ca_df,
                        x="ca",
                        y="segment",
                        orientation="h",
                        color="segment",
                        color_discrete_sequence=segment_palette,
                        labels={"segment": "Segment", "ca": "Chiffre d'affaires"},
                    )
                    fig_bar_ca.update_layout(showlegend=False, margin={"l": 10, "r": 10, "t": 20, "b": 10})
                    st.plotly_chart(fig_bar_ca, use_container_width=True)

                    top_ca = ca_df.iloc[0]
                    st.caption(
                        f"Top CA: **{top_ca['segment']}** ({_fmt_money_ar(top_ca['ca'])})."
                    )
                else:
                    st.info("Aucune donnée de CA par segment.")

        with col2:
            with st.container(border=True):
                st.markdown("### 👥 Clients par segment")
                fig_donut = px.pie(
                    seg_df,
                    names="segment",
                    values="count",
                    hole=0.55,
                    color="segment",
                    color_discrete_sequence=segment_palette,
                )
                fig_donut.update_traces(textposition="inside", texttemplate="%{percent:.1%}")
                fig_donut.update_layout(margin={"l": 10, "r": 10, "t": 20, "b": 10})
                st.plotly_chart(fig_donut, use_container_width=True)

                top_row = seg_df.iloc[0]
                st.caption(
                    f"Segment dominant: **{top_row['segment']}** "
                    f"({_fmt_grouped_int(top_row['count'])} clients, {_fmt_percent(top_row['part'])})."
                )
