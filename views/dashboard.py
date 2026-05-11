import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_all_claims

def render():
    st.markdown('<div class="main-header">Dashboard Analítico</div>', unsafe_allow_html=True)
    
    df = get_all_claims()
    if df.empty:
        st.info("No hay datos suficientes para mostrar el dashboard.")
        return
        
    # Data preprocessing
    df['date_created'] = pd.to_datetime(df['date_created'])
    df['date_closed'] = pd.to_datetime(df['date_closed'])
    df['month_year'] = df['date_created'].dt.strftime('%Y-%m')
    df['day_name'] = df['date_created'].dt.day_name()
    
    # Calculate total resolution time (in days)
    df['resolution_time_days'] = (df['date_closed'] - df['date_created']).dt.total_seconds() / 86400
    
    # KPIs
    total_claims = len(df)
    pending_claims = len(df[df['status'] == 'Pendiente'])
    closed_claims = len(df[df['status'] == 'Cerrado'])
    avg_res_time = df['resolution_time_days'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reclamos", total_claims)
    with col2:
        st.metric("Pendientes", pending_claims)
    with col3:
        st.metric("Cerrados", closed_claims)
    with col4:
        avg_str = f"{avg_res_time:.1f} días" if pd.notna(avg_res_time) else "N/A"
        st.metric("Tiempo Promedio Res.", avg_str)
        
    st.markdown("---")
    
    # Row 1: Time Series & Region
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.subheader("Volumen de Reclamos por Mes")
        vol_mes = df.groupby('month_year').size().reset_index(name='Cantidad')
        vol_mes = vol_mes.sort_values('month_year')
        
        fig1 = px.area(vol_mes, x='month_year', y='Cantidad', 
                       markers=True, 
                       text='Cantidad',
                       labels={'month_year': 'Mes', 'Cantidad': 'Nro Reclamos'},
                       color_discrete_sequence=['#3b82f6'])
        
        fig1.update_traces(textposition='top center', line_shape='spline', fillcolor='rgba(59, 130, 246, 0.2)')
        fig1.update_layout(xaxis_type='category', showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.subheader("AMBA vs Interior")
        if 'region' in df.columns:
            vol_region = df.groupby('region').size().reset_index(name='Cantidad')
            fig2 = px.pie(vol_region, values='Cantidad', names='region', hole=0.4, color_discrete_sequence=['#10b981', '#f59e0b'])
            st.plotly_chart(fig2, use_container_width=True)
            
    # Row 2: Reasons & Ranking
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("Reclamos por Motivo")
        vol_motivo = df.groupby('reason').size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=True)
        fig3 = px.bar(vol_motivo, y='reason', x='Cantidad', orientation='h', color_discrete_sequence=['#6366f1'])
        st.plotly_chart(fig3, use_container_width=True)
        
    with col_chart4:
        st.subheader("Ranking Top 10 Clientes")
        vol_client = df.groupby('client_name').size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=False).head(10)
        fig4 = px.bar(vol_client, x='Cantidad', y='client_name', orientation='h', color_discrete_sequence=['#ec4899'])
        fig4.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("Análisis por Vendedor")
    
    # Filter by Motivo for Salesperson analysis
    motivos_lista = ["Todos"] + sorted(df['reason'].unique().tolist())
    selected_filter_motivo = st.selectbox("Filtrar Análisis por Motivo", motivos_lista)
    
    df_filtered_sales = df.copy()
    if selected_filter_motivo != "Todos":
        df_filtered_sales = df_filtered_sales[df_filtered_sales['reason'] == selected_filter_motivo]
        
    if not df_filtered_sales.empty:
        vol_vendedor = df_filtered_sales.groupby('salesperson').size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=False)
        total_filtered = vol_vendedor['Cantidad'].sum()
        vol_vendedor['Porcentaje'] = (vol_vendedor['Cantidad'] / total_filtered * 100).round(1)
        
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            fig_v = px.bar(vol_vendedor.head(15), x='salesperson', y='Cantidad', 
                           text='Porcentaje', labels={'salesperson': 'Vendedor', 'Cantidad': 'Nro Reclamos'},
                           color='Cantidad', color_continuous_scale='Viridis')
            fig_v.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig_v, use_container_width=True)
        
        with col_v2:
            st.write("**Resumen por Vendedor (Top 10)**")
            st.dataframe(vol_vendedor[['salesperson', 'Cantidad', 'Porcentaje']].head(10), hide_index=True, use_container_width=True)
    else:
        st.info("No hay datos para el motivo seleccionado.")

    st.markdown("---")
    st.subheader("Análisis de Tiempos por Área")
    st.write("Promedio de tiempo (en días) desde la creación del reclamo hasta que se completó cada hito, según los reclamos cerrados o avanzados.")
    
    # Calculate time metrics by area
    time_data = []
    
    # OR -> Tráfico
    if 'or_number_date' in df.columns:
        df['or_date'] = pd.to_datetime(df['or_number_date'])
        trafico_time = (df['or_date'] - df['date_created']).dt.total_seconds() / 86400
        avg_trafico = trafico_time.mean()
        if pd.notna(avg_trafico):
            time_data.append({"Hito": "Orden de Retiro (Tráfico)", "Días Promedio": round(avg_trafico, 1)})
            
    # DPC -> Depósito
    if 'dpc_date' in df.columns:
        df['d_date'] = pd.to_datetime(df['dpc_date'])
        depo_time = (df['d_date'] - df['date_created']).dt.total_seconds() / 86400
        avg_depo = depo_time.mean()
        if pd.notna(avg_depo):
            time_data.append({"Hito": "Ingreso Devolución (Depósito)", "Días Promedio": round(avg_depo, 1)})
            
    # NC -> Facturación
    if 'nc_date' in df.columns:
        df['n_date'] = pd.to_datetime(df['nc_date'])
        fact_time = (df['n_date'] - df['date_created']).dt.total_seconds() / 86400
        avg_fact = fact_time.mean()
        if pd.notna(avg_fact):
            time_data.append({"Hito": "Nota de Crédito (Facturación)", "Días Promedio": round(avg_fact, 1)})
            
    if time_data:
        df_times = pd.DataFrame(time_data)
        fig5 = px.bar(df_times, x='Hito', y='Días Promedio', text_auto=True, color='Hito')
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Aún no hay datos suficientes de fechas registradas para calcular tiempos por área.")
