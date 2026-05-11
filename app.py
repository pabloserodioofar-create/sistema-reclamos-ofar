import streamlit as st
import os

st.set_page_config(page_title="Customer Service - Reclamos", layout="wide", page_icon="📝")

# User Credentials (to be replaced by st.secrets on Streamlit Cloud)
VALID_USER = "admin"
VALID_PASSWORD = "ofar2026"

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 1.5rem;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 5px solid #3b82f6;
        }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 50px;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Authentication Logic
def check_password():
    """Returns `True` if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Show login form
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("Logo Ofar.png", use_container_width=True)
            st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Ingreso al Sistema</h2>", unsafe_allow_html=True)
            with st.form("login_form"):
                user = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("Ingresar", use_container_width=True)
                
                if submit:
                    if user == VALID_USER and password == VALID_PASSWORD:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
        st.markdown('</div>', unsafe_allow_html=True)
    return False

if check_password():
    # Import views
    from views import nuevo_reclamo, pendientes, dashboard, maestros, historial, buscador_clientes

    # Sidebar Logout
    if st.sidebar.button("🔓 Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

    st.sidebar.image("Logo Ofar.png", use_container_width=True)
    st.sidebar.title("Navegación")
    page = st.sidebar.radio("Ir a", [
        "Nuevo Reclamo", 
        "Gestión de Pendientes", 
        "Historial de Reclamos",
        "Buscador de Clientes",
        "Dashboard", 
        "Maestros (Clientes/SKU)"
    ])

    if page == "Nuevo Reclamo":
        nuevo_reclamo.render()
    elif page == "Gestión de Pendientes":
        pendientes.render()
    elif page == "Historial de Reclamos":
        historial.render()
    elif page == "Buscador de Clientes":
        buscador_clientes.render()
    elif page == "Dashboard":
        dashboard.render()
    elif page == "Maestros (Clientes/SKU)":
        maestros.render()
