CREATE DATABASE IF NOT EXISTS inventory_management_system;

USE inventory_management_system;

CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naming VARCHAR(255) NOT NULL,
    quantity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    details TEXT
);

INSERT INTO items (id, naming, quantity) VALUES
(1, 'Item 1', 10),
(2, 'Item 2', 20),
(3, 'Item 3', 30),
(4, 'Item 4', 15),
(5, 'Item 5', 25);

SELECT * FROM items;
SELECT * FROM orders;
