import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'winner_sports.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            payment_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            size TEXT,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bulk_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            sport_type TEXT NOT NULL,
            jersey_count INTEGER NOT NULL,
            shorts_count INTEGER,
            custom_printing TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Football Jersey', 'football', 349, 'High quality polyester football jersey with moisture wicking', 'football_jersey.jpg'),
            ('Football Shorts', 'football', 249, 'Lightweight football shorts with elastic waistband', 'football_shorts.jpg'),
            ('Cricket Jersey', 'cricket', 399, 'Premium cricket jersey with custom name/number printing', 'cricket_jersey.jpg'),
            ('Cricket Shorts', 'cricket', 299, 'Comfortable cricket shorts', 'cricket_shorts.jpg'),
            ('Kabaddi Jersey', 'kabaddi', 329, 'Durable kabaddi jersey for intense matches', 'kabaddi_jersey.jpg'),
            ('Kabaddi Shorts', 'kabaddi', 249, 'Flexible kabaddi shorts', 'kabaddi_shorts.jpg'),
            ('Volleyball Jersey', 'volleyball', 349, 'Breathable volleyball jersey', 'volleyball_jersey.jpg'),
            ('Basketball Jersey', 'basketball', 379, 'Professional basketball jersey with number printing', 'basketball_jersey.jpg'),
            ('Hockey Jersey', 'hockey', 359, 'Durable hockey jersey', 'hockey_jersey.jpg'),
            ('Athletics T-Shirt', 'athletics', 299, 'Lightweight athletics running t-shirt', 'athletics_tshirt.jpg'),
        ]
        cursor.executemany('INSERT INTO products (name, category, price, description, image) VALUES (?,?,?,?,?)', products)

    conn.commit()
    conn.close()
