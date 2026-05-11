import streamlit as st
import pandas as pd
from database import get_clients, get_skus, create_claim
from config import MOTIVOS_RECLAMO

def render():
    st.markdown('<div class="main-header">Crear Nuevo Reclamo</div>', unsafe_allow_html=True)
    
    # Init session state for dynamic articles
    if 'temp_articles' not in st.session_state:
        st.session_state.temp_articles = []
        
    df_clients = get_clients()
    df_skus = get_skus()
    
    # Format for selectbox
    client_list = df_clients['client_id'] + " - " + df_clients['client_name']
    client_list = ["Seleccione un cliente..."] + client_list.tolist()
    
    sku_list = df_skus['article_code'] + " - " + df_skus['article_desc']
    sku_list = ["Seleccione un artículo..."] + sku_list.tolist()
    
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Datos del Reclamo")
        
        selected_client_str = st.selectbox("Cliente", client_list, key="client_selector")
        
        # Auto-region and salesperson logic
        determined_region = "AMBA"
        selected_salesperson = None
        if selected_client_str != "Seleccione un cliente...":
            c_id = selected_client_str.split(" - ")[0]
            client_info = df_clients[df_clients['client_id'] == c_id].iloc[0]
            selected_salesperson = client_info['salesperson']
            distribuidor = client_info['region']
            if distribuidor == "AMBA":
                determined_region = "AMBA"
            else:
                determined_region = "Interior"
            
            st.info(f"📍 **Región Detectada:** {determined_region} (Distribuidor: {distribuidor})")
        
        # Hierarchical Motivo Selection
        categorias = list(MOTIVOS_RECLAMO.keys())
        selected_category = st.selectbox("Categoría de Reclamo", ["Seleccione una categoría..."] + categorias, key="category_selector")
        
        selected_motivo = "Seleccione un motivo..."
        requires_sku = False
        
        if selected_category != "Seleccione una categoría...":
            sub_motivos = list(MOTIVOS_RECLAMO[selected_category].keys())
            selected_sub = st.selectbox("Motivo Específico", ["Seleccione un motivo..."] + sub_motivos, key="subcategory_selector")
            
            if selected_sub != "Seleccione un motivo...":
                selected_motivo = f"{selected_category} - {selected_sub}"
                if "sku" in MOTIVOS_RECLAMO[selected_category][selected_sub]:
                    requires_sku = True
                    
        st.markdown('</div><br>', unsafe_allow_html=True)
        
        if requires_sku:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("Artículos Involucrados")
            st.info("Este motivo requiere que se ingresen los artículos.")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                selected_sku_str = st.selectbox("Artículo (SKU)", sku_list, key="sku_selector")
            with col2:
                unidades = st.number_input("Unidades", min_value=1, step=1, key="unidades_selector")
            with col3:
                st.write("")
                st.write("")
                if st.button("➕ Agregar Artículo", use_container_width=True):
                    if selected_sku_str != "Seleccione un artículo...":
                        code = selected_sku_str.split(" - ")[0]
                        desc = selected_sku_str.split(" - ", 1)[1]
                        st.session_state.temp_articles.append({
                            "code": code,
                            "desc": desc,
                            "units": unidades
                        })
                        st.rerun()
            
            if len(st.session_state.temp_articles) > 0:
                df_temp = pd.DataFrame(st.session_state.temp_articles)
                df_temp.columns = ["Código SKU", "Descripción", "Unidades"]
                st.dataframe(df_temp, use_container_width=True, hide_index=True)
                
                if st.button("Limpiar Artículos"):
                    st.session_state.temp_articles = []
                    st.rerun()
                    
            st.markdown('</div><br>', unsafe_allow_html=True)
            
        st.write("")
        col_gen, col_clear = st.columns([3, 1])
        with col_gen:
            if st.button("🚀 Generar Reclamo", type="primary", use_container_width=True):
                if selected_client_str == "Seleccione un cliente..." or selected_motivo == "Seleccione un motivo...":
                    st.error("Por favor, seleccione un cliente y un motivo.")
                elif requires_sku and len(st.session_state.temp_articles) == 0:
                    st.error("Por favor, agregue al menos un artículo, ya que el motivo lo requiere.")
                else:
                    c_id = selected_client_str.split(" - ")[0]
                    c_name = selected_client_str.split(" - ", 1)[1]
                    
                    claim_id = create_claim(
                        client_id=c_id,
                        client_name=c_name,
                        reason=selected_motivo,
                        region=determined_region,
                        salesperson=selected_salesperson,
                        articles=st.session_state.temp_articles
                    )
                    
                    # Clear session state and widgets
                    st.session_state.temp_articles = []
                    st.session_state.client_selector = "Seleccione un cliente..."
                    st.session_state.category_selector = "Seleccione una categoría..."
                    if "subcategory_selector" in st.session_state:
                        st.session_state.subcategory_selector = "Seleccione un motivo..."
                    
                    st.success(f"✅ Reclamo #{claim_id} generado exitosamente y se encuentra en estado Pendiente.")
                    st.balloons()
                    st.rerun() # Refresh to clear form
        
        with col_clear:
            if st.button("🧹 Limpiar Formulario", use_container_width=True):
                st.session_state.client_selector = "Seleccione un cliente..."
                st.session_state.category_selector = "Seleccione una categoría..."
                if "subcategory_selector" in st.session_state:
                    st.session_state.subcategory_selector = "Seleccione un motivo..."
                if "sku_selector" in st.session_state:
                    st.session_state.sku_selector = "Seleccione un artículo..."
                st.session_state.temp_articles = []
                st.rerun()
