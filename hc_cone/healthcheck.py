from flask import Flask, jsonify
import os
import pika
import threading
import time

app = Flask(__name__)

def consume_health_check():
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
    channel.queue_declare(queue='health_check',durable=True)

    def callback(ch, method, properties, body):
        print(f"[[Health Check] Received: {body.decode()}")
        # You should implement message processing logic here
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='health_check', on_message_callback=callback)
    print('Starting Health Check Consumer...')
    channel.start_consuming()

if __name__ == '__main__':
    threading.Thread(target=consume_health_check, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5001)