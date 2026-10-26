import os
import random
import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "mysql-a844453-nasbak-db.g.aivencloud.com"),
        port=int(os.getenv("DB_PORT", 21778)),
        user=os.getenv("DB_USERNAME", "avnadmin"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE", "defaultdb"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl": {}},
        connect_timeout=10,
    )


@app.route("/", methods=["GET"])
def index():
    return (
        jsonify({"success": True, "message": "Nasbak API Backend Flask is running"}),
        200,
    )


@app.route("/api/orders", methods=["GET"])
def get_orders():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders ORDER BY id DESC")
            orders = cursor.fetchall()
        conn.close()
        return jsonify({"success": True, "data": orders}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    name = data.get("customer_name")
    phone = data.get("customer_phone")
    menu_item = data.get("menu_item", "Nasi Bakar Biasa")
    qty = int(data.get("qty", 1))

    if not name or not phone:
        return (
            jsonify({"success": False, "message": "Nama dan Telepon wajib diisi"}),
            400,
        )

    price_per_item = 14000 if "Paket" in menu_item else 12000
    total_price = price_per_item * qty

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """INSERT INTO orders (customer_name, customer_phone, menu_item, qty, total_price, status, created_at, updated_at) 
                     VALUES (%s, %s, %s, %s, %s, 'pending', NOW(), NOW())"""
            cursor.execute(sql, (name, phone, menu_item, qty, total_price))
            conn.commit()
            order_id = cursor.lastrowid
        conn.close()

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "id": order_id,
                        "customer_name": name,
                        "customer_phone": phone,
                        "menu_item": menu_item,
                        "qty": qty,
                        "total_price": total_price,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/gacha/roll", methods=["POST"])
def roll_gacha():
    data = request.get_json() or {}
    order_id = data.get("order_id")

    if not order_id:
        return jsonify({"success": False, "message": "Order ID diperlukan"}), 400

    rewards = ["Bonus 1 Air Botol", "Diskon Rp 5.000", "Diskon Rp 7.000"]
    selected_reward = random.choice(rewards)

    return jsonify({"success": True, "reward": selected_reward}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
