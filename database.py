import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'claims.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create claims table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    ''')
    
    # Create claim_articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claim_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER,
            article_code TEXT,
            article_desc TEXT,
            units INTEGER,
            FOREIGN KEY(claim_id) REFERENCES claims(id)
        )
    ''')

    # Create clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            client_name TEXT,
            salesperson TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            region TEXT
        )
    ''')

    # Create skus table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skus (
            article_code TEXT PRIMARY KEY,
            article_desc TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_clients():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df

def get_skus():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM skus", conn)
    conn.close()
    return df

def add_client(client_id, client_name, salesperson=None, address=None, phone=None, email=None, region=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO clients (client_id, client_name, salesperson, address, phone, email, region) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (client_id, client_name, salesperson, address, phone, email, region))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def add_sku(article_code, article_desc):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO skus (article_code, article_desc) VALUES (?, ?)", (article_code, article_desc))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def create_claim(client_id, client_name, reason, region, salesperson, articles):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO claims (date_created, client_id, client_name, reason, region, salesperson, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
    ''', (now, client_id, client_name, reason, region, salesperson))
    
    claim_id = cursor.lastrowid
    
    for art in articles:
        cursor.execute('''
            INSERT INTO claim_articles (claim_id, article_code, article_desc, units)
            VALUES (?, ?, ?, ?)
        ''', (claim_id, art['code'], art['desc'], art['units']))
        
    conn.commit()
    conn.close()
    return claim_id

def get_pending_claims():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM claims WHERE status = 'Pendiente'", conn)
    conn.close()
    return df

def get_closed_claims():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM claims WHERE status = 'Cerrado' ORDER BY date_closed DESC", conn)
    conn.close()
    return df

def get_all_claims():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM claims", conn)
    conn.close()
    return df

def get_claim_articles(claim_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM claim_articles WHERE claim_id = ?", conn, params=(claim_id,))
    conn.close()
    return df

def update_claim_field(claim_id, field_name, value):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # Update both the field and its corresponding date
    query = f"UPDATE claims SET {field_name} = ?, {field_name}_date = ? WHERE id = ?"
    cursor.execute(query, (value, now, claim_id))
    
    conn.commit()
    conn.close()

def close_claim(claim_id):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("UPDATE claims SET status = 'Cerrado', date_closed = ? WHERE id = ?", (now, claim_id))
    
    conn.commit()
    conn.close()
