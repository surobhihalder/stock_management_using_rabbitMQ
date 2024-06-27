from flask import Flask, jsonify, request
import mysql.connector
import os
import pika
import threading
import time
import json

app = Flask(__name__)

def consume_item_creation():
    amqp_url = os.getenv('AMQP_URL', 'amqp://guest:guest@localhost:5672/')
    url_params = pika.URLParameters(amqp_url)
    url_params.heartbeat = 30 

    while True:
        try:
            connection = pika.BlockingConnection(url_params)
            break
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed. Retrying...")
            time.sleep(5)
    
    channel = connection.channel()
    channel.queue_declare(queue='item_creation', durable=True)

    def callback(ch, method, properties, body):
        print(f"[Item Creation] Received: {body.decode()}")
        item_data = json.loads(body.decode())

        try:
            with mysql.connector.connect(
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', '9900787101'),
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'inventory_management_system')
            ) as db:
                with db.cursor() as cursor:
                    query = "INSERT INTO items (id, naming, quantity) VALUES (%s, %s, %s)"
                    cursor.execute(query, (item_data['id'], item_data['naming'], item_data['quantity']))
                    db.commit()
                    print(f"Item created: {item_data['naming']}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)  
        except Exception as e:
            print(f"Failed to insert item into database: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue='item_creation', on_message_callback=callback, auto_ack=False)
    print('Starting Item Creation Consumer...')
    channel.start_consuming()

if __name__ == '__main__':
    threading.Thread(target=consume_item_creation, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5002)
