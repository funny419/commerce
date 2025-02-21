from flask import Flask, request, jsonify
from flask_cors import CORS

import pymysql
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS
CORS(app)

# MaridDB Connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

# 회원가입 API
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password_hash = data.get('password_hash')  # 프론트엔드에서 해시 처리된 값
    full_name = data.get('full_name')
    address = data.get('address')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    country = data.get('country')
    phone_number = data.get('phone_number')
    date_of_birth = data.get('date_of_birth')

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO users (
                username, email, password_hash, full_name, address, city, state,
                postal_code, country, phone_number, date_of_birth
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                username, email, password_hash, full_name, address, city, state,
                postal_code, country, phone_number, date_of_birth
            ))
            connection.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        connection.close()

@app.route('/api/check-username', methods=['GET'])
def check_username():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return jsonify({"available": result is None}), 200
    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/check-email', methods=['GET'])
def check_email():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            return jsonify({"available": result is None}), 200
    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()