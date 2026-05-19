import pandas as pd
import os
from database import init_db, add_client, add_sku

def migrate_excel_to_sqlite():
    print("Initializing database...")
    init_db()
    
    excel_file = "clientes+sku.xlsx"
    if not os.path.exists(excel_file):
        print(f"Excel file {excel_file} not found. Skipping data migration.")
        return

    print("Loading data from Excel...")
    xl = pd.ExcelFile(excel_file)
    
    if 'CLIENTES' in xl.sheet_names:
        df_clients = xl.parse('CLIENTES')
        df_clients.columns = [str(c).strip() for c in df_clients.columns]
        
        if len(df_clients.columns) >= 10:
            df_clients = df_clients.iloc[:, [0, 1, 2, 3, 7, 8, 9]]
            df_clients.columns = ['client_id', 'client_name', 'salesperson', 'address', 'phone', 'email', 'region']
            
            for col in df_clients.columns:
                df_clients[col] = df_clients[col].astype(str).str.strip().replace('nan', None)
            
            df_clients = df_clients.drop_duplicates(subset=['client_id'])
            
            added = 0
            for _, row in df_clients.iterrows():
                success = add_client(
                    row['client_id'], row['client_name'], row['salesperson'], 
                    row['address'], row['phone'], row['email'], row['region']
                )
                if success:
                    added += 1
                    
            print(f"Imported {added} clients with full details.")

    if 'SKU' in xl.sheet_names:
        df_skus = xl.parse('SKU')
        df_skus.columns = [str(c).strip() for c in df_skus.columns]
        
        if len(df_skus.columns) >= 2:
            df_skus = df_skus.iloc[:, :2]
            df_skus.columns = ['article_code', 'article_desc']
            df_skus['article_code'] = df_skus['article_code'].astype(str).str.strip()
            df_skus['article_code'] = df_skus['article_code'].str.replace('.0', '', regex=False)
            df_skus['article_desc'] = df_skus['article_desc'].astype(str).str.strip()
            df_skus = df_skus.drop_duplicates(subset=['article_code'])
            
            added = 0
            for _, row in df_skus.iterrows():
                success = add_sku(row['article_code'], row['article_desc'])
                if success:
                    added += 1
            print(f"Imported {added} SKUs.")
            
    print("Migration complete.")

if __name__ == "__main__":
    migrate_excel_to_sqlite()
