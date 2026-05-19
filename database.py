from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
import streamlit as st
import os

def get_engine():
    # Use DIRECT_URL for migrations/writes if possible, else DATABASE_URL
    try:
        # Pgbouncer URL works fine for SQLAlchemy if pool_pre_ping is True, but DIRECT_URL is safer for schema changes
        db_url = st.secrets.get("DIRECT_URL", st.secrets.get("DATABASE_URL", ""))
    except Exception:
        db_url = os.environ.get("DIRECT_URL", os.environ.get("DATABASE_URL", ""))
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    return create_engine(db_url, pool_pre_ping=True)

def init_db():
    engine = get_engine()
    
    with engine.begin() as conn:
        # Create claims table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS claims (
                id SERIAL PRIMARY KEY,
                date_created TEXT,
                client_id TEXT,
                client_name TEXT,
                reason TEXT,
                region TEXT,
                status TEXT,
                date_closed TEXT,
                rto TEXT, rto_date TEXT,
                nic TEXT, nic_date TEXT,
                or_number TEXT, or_number_date TEXT,
                dpc TEXT, dpc_date TEXT,
                nc TEXT, nc_date TEXT,
                fc TEXT, fc_date TEXT,
                rta TEXT, rta_date TEXT,
                pdf TEXT, pdf_date TEXT,
                reclamo TEXT, reclamo_date TEXT,
                seguimiento TEXT, seguimiento_date TEXT,
                siniestro_dev TEXT, siniestro_dev_date TEXT,
                reclamo_cds TEXT, reclamo_cds_date TEXT,
                resolucion_solicitud TEXT, resolucion_solicitud_date TEXT,
                doc_cds TEXT, doc_cds_date TEXT,
                rto_manual TEXT, rto_manual_date TEXT,
                salesperson TEXT
            )
        '''))
        
        # Create claim_articles table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS claim_articles (
                id SERIAL PRIMARY KEY,
                claim_id INTEGER REFERENCES claims(id) ON DELETE CASCADE,
                article_code TEXT,
                article_desc TEXT,
                units INTEGER
            )
        '''))

        # Create clients table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                client_name TEXT,
                salesperson TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                region TEXT
            )
        '''))

        # Create skus table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS skus (
                article_code TEXT PRIMARY KEY,
                article_desc TEXT
            )
        '''))

def get_clients():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM clients", engine)

def get_skus():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM skus", engine)

def add_client(client_id, client_name, salesperson=None, address=None, phone=None, email=None, region=None):
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO clients (client_id, client_name, salesperson, address, phone, email, region) 
                VALUES (:id, :name, :sp, :addr, :phone, :email, :region)
                ON CONFLICT (client_id) DO UPDATE SET 
                client_name = EXCLUDED.client_name,
                salesperson = EXCLUDED.salesperson,
                address = EXCLUDED.address,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                region = EXCLUDED.region
            """), {
                "id": client_id, "name": client_name, "sp": salesperson, 
                "addr": address, "phone": phone, "email": email, "region": region
            })
        return True
    except Exception as e:
        print(f"Error adding client: {e}")
        return False

def add_sku(article_code, article_desc):
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO skus (article_code, article_desc) 
                VALUES (:code, :desc)
                ON CONFLICT (article_code) DO NOTHING
            """), {"code": article_code, "desc": article_desc})
        return True
    except Exception as e:
        print(f"Error adding SKU: {e}")
        return False

def create_claim(client_id, client_name, reason, region, salesperson, articles):
    engine = get_engine()
    now = datetime.now().isoformat()
    
    with engine.begin() as conn:
        result = conn.execute(text('''
            INSERT INTO claims (date_created, client_id, client_name, reason, region, salesperson, status)
            VALUES (:date, :cid, :cname, :reason, :region, :sp, 'Pendiente')
            RETURNING id
        '''), {
            "date": now, "cid": client_id, "cname": client_name, 
            "reason": reason, "region": region, "sp": salesperson
        })
        
        claim_id = result.scalar()
        
        for art in articles:
            conn.execute(text('''
                INSERT INTO claim_articles (claim_id, article_code, article_desc, units)
                VALUES (:cid, :code, :desc, :units)
            '''), {
                "cid": claim_id, "code": art['code'], "desc": art['desc'], "units": art['units']
            })
            
    return claim_id

def get_pending_claims():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM claims WHERE status = 'Pendiente'", engine)

def get_closed_claims():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM claims WHERE status = 'Cerrado' ORDER BY date_closed DESC", engine)

def get_all_claims():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM claims", engine)

def get_claim_articles(claim_id):
    engine = get_engine()
    return pd.read_sql_query(
        text("SELECT * FROM claim_articles WHERE claim_id = :id"), 
        engine, 
        params={"id": claim_id}
    )

def update_claim_field(claim_id, field_name, value):
    engine = get_engine()
    now = datetime.now().isoformat()
    
    with engine.begin() as conn:
        query = text(f"UPDATE claims SET {field_name} = :val, {field_name}_date = :now WHERE id = :id")
        conn.execute(query, {"val": value, "now": now, "id": claim_id})

def close_claim(claim_id):
    engine = get_engine()
    now = datetime.now().isoformat()
    
    with engine.begin() as conn:
        conn.execute(text("UPDATE claims SET status = 'Cerrado', date_closed = :now WHERE id = :id"), 
                    {"now": now, "id": claim_id})
