from flask import Flask, jsonify

app = Flask(__name__)

# Mock Database (Simple Python Dictionary)
INVENTORY_DATA = {
    "WH-1000XM5": {"stock": 50, "location": "Warehouse A"},
    "AirPods Pro 2": {"stock": 12, "location": "Warehouse B"},
    "Bose QC Ultra": {"stock": 0, "location": "Warehouse C"},
    "Galaxy Buds 2": {"stock": 200, "location": "Warehouse A"},
}

@app.route('/inventory/<product_id>', methods=['GET'])
def get_inventory(product_id):
    """
    API endpoint to check inventory for a specific product ID.
    Example: GET http://127.0.0.1:5000/inventory/WH-1000XM5
    """
    product_data = INVENTORY_DATA.get(product_id)

    if product_data is None:
        return jsonify({
            "product_id": product_id,
            "status": "error",
            "message": "Product ID not found."
        }), 404
    
    # Return the inventory data as JSON
    return jsonify({
        "product_id": product_id,
        "stock_level": product_data["stock"],
        "status": "success"
    }), 200

if __name__ == '__main__':
    # Run the server on the default port 5000
    print("Flask API running at http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)