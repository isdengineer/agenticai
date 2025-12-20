CREATE TABLE customer_orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    product VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    status ENUM('Shipped', 'Pending', 'Cancelled') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO customer_orders (customer_name, product, quantity, status) VALUES
('Alice Johnson', 'Laptop Pro', 1, 'Shipped'),
('Bob Williams', 'Monitor 4K', 2, 'Pending'),
('Alice Johnson', 'Webcam HD', 1, 'Shipped'),
('Charlie Davis', 'Keyboard RGB', 5, 'Pending'),
('Charlie Davis', 'Mouse Wireless', 3, 'Shipped');