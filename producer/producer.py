from flask import Flask, jsonify, request
import pika
import os
import mysql.connector
import json

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '9900787101'),
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'inventory_management_system')
    )

def get_rabbitmq_channel():
    amqp_url = os.getenv('AMQP_URL', 'amqp://guest:guest@rabbitmq:5672/')
    url_params = pika.URLParameters(amqp_url)
    url_params.heartbeat = 30
    connection = pika.BlockingConnection(url_params)
    return connection.channel()

def produce_message(queue_name, message):
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Published message to {queue_name}: {message}")
    except Exception as e:
        print(f"Failed to publish message to {queue_name}: {e}")
    finally:
        if 'channel' in locals():
            channel.close()

@app.route('/health', methods=['GET'])
def health_check():
    
    produce_message('health_check', "Health Check Ping")
    return jsonify({"status": "healthy"}), 200

@app.route('/item', methods=['POST'])
def create_item():
    data = request.json
    produce_message('item_creation', json.dumps(data))
    return jsonify({"status": "Data sent to queue for item creation"}), 202

@app.route('/inventory/<int:item_id>/stock', methods=['PUT'])
def update_stock(item_id):
    data = request.json
    message = json.dumps({"action": "update", "id": item_id, "data": data})
    produce_message('stock_management', message)
    return jsonify({"status": "Update request sent to queue"}), 202

@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    message = json.dumps({"action": "delete", "id": item_id})
    produce_message('stock_management', message)
    return jsonify({"status": "Delete request sent to queue"}), 202

@app.route('/order', methods=['POST'])
def create_order():
    order_details = request.json
    produce_message('order_processing', json.dumps(order_details))
    return jsonify({"status": "Order request sent to queue"}), 202

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
