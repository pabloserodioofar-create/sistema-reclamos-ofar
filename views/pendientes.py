import streamlit as st
import pandas as pd
from database import get_pending_claims, update_claim_field, close_claim, get_claim_articles
from config import MOTIVOS_RECLAMO, FIELD_LABELS

def render():
    st.markdown('<div class="main-header">Gestión de Reclamos Pendientes</div>', unsafe_allow_html=True)
    
    df_pending = get_pending_claims()
    
    if df_pending.empty:
        st.info("No hay reclamos pendientes en este momento. 🎉")
        return
        
    st.write(f"Total de reclamos pendientes: **{len(df_pending)}**")
    
    # Display table of pending claims
    display_cols = ['id', 'date_created', 'client_id', 'client_name', 'reason', 'region']
    df_display = df_pending[display_cols].copy()
    df_display.columns = ['ID', 'Fecha Creación', 'Cód. Cliente', 'Cliente', 'Motivo', 'Región']
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("Actualizar Reclamo")
    
    # Select claim to edit
    claim_ids = df_pending['id'].tolist()
    selected_id = st.selectbox("Seleccione el ID del reclamo a actualizar", ["Seleccione..."] + claim_ids)
    
    if selected_id != "Seleccione...":
        claim_data = df_pending[df_pending['id'] == selected_id].iloc[0]
        reason = claim_data['reason']
        
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"#### Reclamo #{selected_id} - {claim_data['client_name']}")
        st.write(f"**Motivo:** {reason}")
        
        # Get required fields from nested structure
        required_fields = []
        requires_sku = False
        if " - " in reason:
            cat, sub = reason.split(" - ", 1)
            if cat in MOTIVOS_RECLAMO and sub in MOTIVOS_RECLAMO[cat]:
                required_fields = MOTIVOS_RECLAMO[cat][sub]
                if "sku" in required_fields:
                    requires_sku = True
        
        # Check articles if required
        if requires_sku:
            df_arts = get_claim_articles(selected_id)
            if not df_arts.empty:
                st.write("**Artículos:**")
                st.dataframe(df_arts[['article_code', 'article_desc', 'units']], hide_index=True)
        
        st.markdown("---")
        st.markdown("##### Completar información requerida")
        
        fields_to_fill = [f for f in required_fields if f != 'sku']
        
        if not fields_to_fill:
            st.info("Este motivo no requiere información adicional.")
        
        all_filled = True
        
        with st.form(f"update_form_{selected_id}"):
            for field in fields_to_fill:
                current_val = claim_data[field] if pd.notna(claim_data[field]) else ""
                label = FIELD_LABELS.get(field, field.upper())
                
                # Check if it's empty to decide if all are filled
                if not current_val:
                    all_filled = False
                
                new_val = st.text_input(label, value=current_val, key=f"input_{field}")
                
            col1, col2 = st.columns(2)
            with col1:
                submit_update = st.form_submit_button("💾 Guardar Cambios Parciales", use_container_width=True)
            with col2:
                # Disable the close button if not all fields are filled
                close_disabled = not all_filled
                submit_close = st.form_submit_button("🔒 Cerrar Reclamo", disabled=close_disabled, use_container_width=True)
                
            if submit_update:
                for field in fields_to_fill:
                    # Get value from session state
                    val = st.session_state[f"input_{field}"]
                    current = claim_data[field] if pd.notna(claim_data[field]) else ""
                    if val != current:
                        update_claim_field(selected_id, field, val)
                st.success("Cambios guardados correctamente.")
                st.rerun()
                
            if submit_close:
                if all_filled:
                    close_claim(selected_id)
                    st.success(f"Reclamo #{selected_id} cerrado exitosamente.")
                    st.rerun()
                else:
                    st.error("No se puede cerrar el reclamo hasta que se completen todos los campos requeridos.")
                    
        if not all_filled:
            st.warning("Debe completar todos los campos requeridos arriba para poder cerrar este reclamo.")
            
        st.markdown('</div>', unsafe_allow_html=True)
