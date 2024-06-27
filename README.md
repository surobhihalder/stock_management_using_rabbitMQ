docker-compose build
docker-compose up

open rabbitmqmanagementui

python producer.py
produce queue

curl -X GET http://localhost:5000/health

curl -X POST http://localhost:5000/item -H "Content-Type: application/json" -d "{\"id\": 6, \"naming\": \"Item 6\", \"quantity\": 40}"

curl -X PUT http://localhost:5000/inventory/6/stock -H "Content-Type: application/json" -d "{\"naming\": \"Item 6\",\"quantity\": 50}"

curl -X POST http://localhost:5000/order -H "Content-Type: application/json" -d "{\"order_id\": 1, \"items\": [{\"id\": 1, \"quantity\": 5}, {\"id\": 2, \"quantity\": 10}]}"

curl -X DELETE http://localhost:5000/inventory/6
