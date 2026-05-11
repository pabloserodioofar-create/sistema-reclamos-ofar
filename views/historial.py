import streamlit as st
import pandas as pd
from database import get_closed_claims, get_claim_articles
from config import FIELD_LABELS

def render():
    st.markdown('<div class="main-header">Historial de Reclamos Cerrados</div>', unsafe_allow_html=True)
    
    df_closed = get_closed_claims()
    
    if df_closed.empty:
        st.info("No hay reclamos cerrados para mostrar.")
        return
        
    # Search Filter
    search_query = st.text_input("🔍 Buscar por Cliente (Nombre o ID)", "").lower()
    
    if search_query:
        df_closed = df_closed[
            df_closed['client_name'].str.lower().contains(search_query, na=False) |
            df_closed['client_id'].str.lower().contains(search_query, na=False)
        ]
        
    st.write(f"Resultados: **{len(df_closed)}**")
    
    if df_closed.empty:
        st.warning("No se encontraron resultados para su búsqueda.")
        return

    # Display basic info in a table
    display_cols = ['id', 'date_created', 'date_closed', 'client_id', 'client_name', 'reason']
    df_display = df_closed[display_cols].copy()
    df_display.columns = ['ID', 'Creado', 'Cerrado', 'Cód. Cliente', 'Cliente', 'Motivo']
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("Detalle del Reclamo")
    
    selected_id = st.selectbox("Seleccione un ID para ver toda la información", ["Seleccione..."] + df_closed['id'].tolist())
    
    if selected_id != "Seleccione...":
        claim = df_closed[df_closed['id'] == selected_id].iloc[0]
        
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**ID:** {claim['id']}")
            st.write(f"**Cliente:** {claim['client_name']} ({claim['client_id']})")
            st.write(f"**Motivo:** {claim['reason']}")
            st.write(f"**Región:** {claim['region']}")
        with col2:
            st.write(f"**Fecha Creación:** {claim['date_created']}")
            st.write(f"**Fecha Cierre:** {claim['date_closed']}")
            
        st.markdown("---")
        st.markdown("##### Información de Resolución")
        
        # Display all filled fields based on FIELD_LABELS
        res_cols = st.columns(2)
        idx = 0
        for field, label in FIELD_LABELS.items():
            if field == 'sku': continue
            val = claim[field] if field in claim and pd.notna(claim[field]) else None
            date_val = claim[f"{field}_date"] if f"{field}_date" in claim and pd.notna(claim[f"{field}_date"]) else None
            
            if val:
                with res_cols[idx % 2]:
                    st.write(f"**{label}:** {val}")
                    if date_val:
                        st.caption(f"Registrado el: {date_val}")
                idx += 1
        
        # Display Articles
        df_arts = get_claim_articles(selected_id)
        if not df_arts.empty:
            st.markdown("---")
            st.markdown("##### Artículos Involucrados")
            st.dataframe(df_arts[['article_code', 'article_desc', 'units']], hide_index=True, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
