import streamlit as st
import pandas as pd
from database import get_clients

def render():
    st.markdown('<div class="main-header">Buscador de Clientes</div>', unsafe_allow_html=True)
    
    df_clients = get_clients()
    
    # Format for selectbox autocomplete
    client_options = df_clients['client_id'] + " - " + df_clients['client_name']
    client_options = ["Seleccione un cliente para ver detalles..."] + client_options.tolist()
    
    selected_client_str = st.selectbox("🔍 Buscar Cliente (Empiece a escribir...)", client_options)
    
    if selected_client_str != "Seleccione un cliente para ver detalles...":
        c_id = selected_client_str.split(" - ")[0]
        client = df_clients[df_clients['client_id'] == c_id].iloc[0]
        
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"### {client['client_id']} - {client['client_name']}")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 📍 Ubicación y Zona")
            st.markdown(f"**Dirección:** {client['address'] if client['address'] else 'No disponible'}")
            st.markdown(f"**Distribuidor:** {client['region'] if client['region'] else 'No disponible'}")
            st.markdown(f"**Zona:** {client['region'] if client['region'] else 'No disponible'}") # Using region as distributor/zone
            
        with col2:
            st.markdown(f"#### 📞 Contacto y Ventas")
            st.markdown(f"**Teléfono:** {client['phone'] if client['phone'] else 'No disponible'}")
            st.markdown(f"**Email:** {client['email'] if client['email'] else 'No disponible'}")
            st.markdown(f"**Vendedor:** {client['salesperson'] if client['salesperson'] else 'No disponible'}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Utilice el buscador arriba para localizar un cliente y ver su información de contacto y logística.")
