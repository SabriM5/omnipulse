import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    
    cur = conn.cursor()
    create_users_query = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(150) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """ 
    create_sellers_query = """
        CREATE TABLE IF NOT EXISTS sellers(
            seller_id SERIAL PRIMARY KEY,
            company_name VARCHAR(50),
            commission_rate DECIMAL(4,2)
        );
        """ 
    create_products_query = """
        CREATE TABLE IF NOT EXISTS products(
            product_id SERIAL PRIMARY KEY,
            seller_id INTEGER REFERENCES sellers(seller_id),
            name VARCHAR(50),
            price DECIMAL(10,2)
        );
        """ 
    create_orders_query = """
        CREATE TABLE IF NOT EXISTS orders(
            order_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """ 
    create_order_items_query="""
        CREATE TABLE IF NOT EXISTS order_items(
            order_item_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER,
            unit_price DECIMAL(10,2)
        );""" 

    cur.execute(create_users_query)
    cur.execute(create_sellers_query)
    cur.execute(create_products_query)
    cur.execute(create_orders_query)
    cur.execute(create_order_items_query)
    
    conn.commit()
    print(" Toutes les tables de la Marketplace ont été créées avec succès !")
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Erreur SQL : {e}")