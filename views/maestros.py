import streamlit as st
from database import get_clients, get_skus, add_client, add_sku

def render():
    st.markdown('<div class="main-header">Maestros: Clientes y Artículos</div>', unsafe_allow_html=True)
    st.write("Administra los datos base que alimentan los selectores de los reclamos.")
    
    tab1, tab2 = st.tabs(["👥 Clientes", "📦 Artículos (SKU)"])
    
    with tab1:
        st.subheader("Agregar Nuevo Cliente")
        with st.form("form_nuevo_cliente", clear_on_submit=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                c_id = st.text_input("Código de Cliente")
                salesperson = st.text_input("Vendedor")
                phone = st.text_input("Teléfono")
            with col2:
                c_name = st.text_input("Razón Social")
                address = st.text_input("Dirección")
                email = st.text_input("Email")
            
            region = st.selectbox("Región (Distribuidor)", ["AMBA", "Interior", "1-Cruz Del Sur", "2-Andreani", "Otros"])
            
            submit_client = st.form_submit_button("Guardar Cliente", use_container_width=True)
            if submit_client:
                if c_id and c_name:
                    success = add_client(c_id, c_name, salesperson, address, phone, email, region)
                    if success:
                        st.success(f"Cliente '{c_name}' agregado correctamente.")
                    else:
                        st.error(f"El código '{c_id}' ya existe.")
                else:
                    st.warning("Debe completar todos los campos obligatorios (Código y Razón Social).")
                    
        st.divider()
        st.subheader("Directorio de Clientes")
        df_clients = get_clients()
        st.dataframe(df_clients, use_container_width=True, hide_index=True)
        
    with tab2:
        st.subheader("Agregar Nuevo Artículo")
        with st.form("form_nuevo_sku", clear_on_submit=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                s_id = st.text_input("Código Artículo (SKU)")
            with col2:
                s_desc = st.text_input("Descripción")
            
            submit_sku = st.form_submit_button("Guardar Artículo", use_container_width=True)
            if submit_sku:
                if s_id and s_desc:
                    success = add_sku(s_id, s_desc)
                    if success:
                        st.success(f"Artículo '{s_desc}' agregado correctamente.")
                    else:
                        st.error(f"El artículo '{s_id}' ya existe.")
                else:
                    st.warning("Debe completar todos los campos.")
                    
        st.divider()
        st.subheader("Catálogo de Artículos")
        df_skus = get_skus()
        st.dataframe(df_skus, use_container_width=True, hide_index=True)
