import os
import random
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from dotenv import load_dotenv

load_dotenv()
fake = Faker('fr_FR')

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE order_items, orders, products, sellers, users RESTART IDENTITY CASCADE;")
    print(" Début de la génération des données")

    # ==========================================
    # 1. GÉNÉRATION DES UTILISATEURS (USERS)
    # ==========================================
    users_data = []
    for _ in range(100): 
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        users_data.append((first_name, last_name, email))

    execute_values(
        cur,
        "INSERT INTO users (first_name, last_name, email) VALUES %s",
        users_data
    )
    print("100 Utilisateurs insérés.")

    # ==========================================
    # 2. GÉNÉRATION DES VENDEURS (SELLERS)
    # ==========================================
    sellers_data = []
    for _ in range(10): # On veut 10 vendeurs
        company_name= fake.company()
        commission_rate = random.uniform(0.05, 0.20)
        sellers_data.append((company_name,commission_rate))
        pass

    execute_values( cur, "INSERT INTO sellers (company_name,commission_rate) VALUES %s", sellers_data )
    
    print("10 Vendeurs insérés.")

    # ==========================================
    # 3. GÉNÉRATION DES PRODUITS (PRODUCTS)
    # ==========================================
    # Pour attribuer un seller_id existant, on triche proprement : 
    # Puisque nos vendeurs viennent d'être créés et que leurs ID sont auto-incrémentés de 1 à 10...
    # Leurs ID sont littéralement [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] !
    
    products_data = []
    for _ in range(50):
        seller_id = random.randint(1, 10)
        name = fake.word()
        price=random.uniform(10.0, 500.0)
        products_data.append((seller_id,name,price))
        pass

    execute_values(cur, "INSERT INTO products (seller_id,name,price) VALUES %s", products_data)

    print("50 Produits insérés.")

    # ==========================================
    # 4. GÉNÉRATION DES COMMANDES (ORDERS)
    # ==========================================
    statuses = ['DELIVERED', 'SHIPPED', 'PENDING', 'CANCELLED']
    # On donne plus de poids à DELIVERED (70% des commandes) pour que ce soit réaliste
    status_weights = [0.70, 0.15, 0.10, 0.05]

    orders_data = []
    for _ in range(500):
        user_id = random.randint(1,100)
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        created_at = fake.date_time_between(start_date='-90d', end_date='now')
        orders_data.append((user_id, status, created_at))

    execute_values(
        cur,
        "INSERT INTO orders (user_id, status, created_at) VALUES %s",
        orders_data
    )
    print("500 Commandes insérées.")

    # ==========================================
    # 5. GÉNÉRATION DES LIGNES DE COMMANDE (ORDER_ITEMS)
    # ==========================================
    order_items_data = []
    for order_id in range(1, 501):
        nb_items = random.randint(1, 4)
        chosen_products = random.sample(range(1, 51), k=nb_items)
        for product_id in chosen_products:
            quantity = random.randint(1,3)
            unit_price = round(products_data[product_id - 1][2], 2)
            order_items_data.append((order_id, product_id, quantity, unit_price))

    execute_values(cur, "INSERT INTO order_items(order_id, product_id, quantity, unit_price) VALUES %s",order_items_data)

    print(f"{len(order_items_data)} Lignes de commandes insérées.")

    conn.commit()
    cur.close()
    conn.close()

except Exception as e:
    print(f"Erreur : {e}")