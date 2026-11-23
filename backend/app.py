import os
import time
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "orderpulse"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
    )

def init_db():
    for _ in range(10):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS menu (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INT NOT NULL
                )""")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    item_id INT NOT NULL,
                    quantity INT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PLACED'
                )""")
            cur.execute("SELECT COUNT(*) FROM menu")
            if cur.fetchone()[0] == 0:
                cur.execute("""
                    INSERT INTO menu (name, price) VALUES
                    ('Chicken Biryani', 180),
                    ('Masala Dosa', 80),
                    ('Parotta', 40),
                    ('Filter Coffee', 30)""")
            conn.commit()
            cur.close()
            conn.close()
            return
        except Exception as e:
            print("DB not ready, retrying...", e)
            time.sleep(3)

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/menu")
def menu():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM menu ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "price": r[2]} for r in rows])

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (item_id, quantity) VALUES (%s, %s) RETURNING id",
        (data["item_id"], data["quantity"]),
    )
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(order_id=order_id, status="PLACED"), 201

@app.route("/orders/<int:order_id>")
def get_order(order_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, item_id, quantity, status FROM orders WHERE id=%s", (order_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if not r:
        return jsonify(error="not found"), 404
    return jsonify(id=r[0], item_id=r[1], quantity=r[2], status=r[3])

# Test endpoints for AIOps demo (later phases)
@app.route("/slow")
def slow():
    time.sleep(5)
    return jsonify(message="slow response")

@app.route("/crash")
def crash():
    return jsonify(error="simulated failure"), 500

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)