from flask import Flask, jsonify, request
import mysql.connector
import os
import pika
import threading
import time
import json

app = Flask(__name__)
def handle_update(message):
    item_id = message["id"]
    data = message["data"]
    try:
        db = mysql.connector.connect(
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '9900787101'),
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'inventory_management_system')
        )
        cursor = db.cursor()
        query = "UPDATE items SET naming = %s, quantity = %s WHERE id = %s"
        cursor.execute(query, (data['naming'], data['quantity'], item_id))
        db.commit()
        print(f"Updated item {item_id} with name {data['naming']} and quantity {data['quantity']}")
    except Exception as e:
        print(f"Failed to update item {item_id}: {e}")
    finally:
        cursor.close()
        db.close()

def handle_delete(message):
    item_id = message["id"]
    try:
        db = mysql.connector.connect(
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '9900787101'),
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'inventory_management_system')
        )
        cursor = db.cursor()
        query = "DELETE FROM items WHERE id = %s"
        cursor.execute(query, (item_id,))
        db.commit()
        print(f"Deleted item {item_id}")
    except Exception as e:
        print(f"Failed to delete item {item_id}: {e}")
    finally:
        cursor.close()
        db.close()
def consume_stock_management():
    amqp_url = os.getenv('AMQP_URL', 'amqp://guest:guest@localhost:5672/')
    url_params = pika.URLParameters(amqp_url)
    
    while True:
        try:
            connection = pika.BlockingConnection(url_params)
            break
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed. Retrying...")
            time.sleep(5)
    
    channel = connection.channel()
    channel.queue_declare(queue='stock_management',durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        action = message["action"]

        if action == "update":
            handle_update(message)
        elif action == "delete":
            handle_delete(message)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='stock_management', on_message_callback=callback, auto_ack=False)
    print('Starting Stock Management Consumer...')
    channel.start_consuming()

if __name__ == '__main__':
    threading.Thread(target=consume_stock_management, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5003)
