from flask import Flask, jsonify, request
import mysql.connector
import os
import pika
import json
import threading
import time
app = Flask(__name__)

def consume_order_processing():
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
    channel.queue_declare(queue='order_processing',durable=True)

    def callback(ch, method, properties, body):
        print(f"[Order Processing] Received: {body.decode()}")
        order_details = json.loads(body.decode())
        process_order(order_details)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='order_processing', on_message_callback=callback, auto_ack=True)
    print('Starting Order Processing Consumer...')
    channel.start_consuming()


def process_order(order_details):

    db = mysql.connector.connect(
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '9900787101'),
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'inventory_management_system')
    )
    cursor = db.cursor()

    
    for item in order_details.get('items', []):
        item_id = item.get('id')
        quantity_ordered = item.get('quantity')

        
        cursor.execute("SELECT quantity FROM items WHERE id = %s", (item_id,))
        item_data = cursor.fetchone()
        if item_data and item_data[0] >= quantity_ordered:
            
            cursor.execute("UPDATE items SET quantity = quantity - %s WHERE id = %s", (quantity_ordered, item_id))
        else:
            print(f"Item {item_id} does not have enough stock.")
            db.rollback()
            cursor.close()
            db.close()
            return {"status": "error", "message": "Not enough stock for one or more items"}

    db.commit()

    
    cursor.execute("INSERT INTO orders (order_id, details) VALUES (%s, %s)", 
                   (order_details.get('order_id'), json.dumps(order_details)))

    db.commit()
    cursor.close()
    db.close()

    return {"status": "success", "message": "Order processed successfully"}


if __name__ == '__main__':
    threading.Thread(target=consume_order_processing, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5004)
