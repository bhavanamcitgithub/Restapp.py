from flask import Flask, jsonify, request, abort
import sqlite3

app = Flask(_name_)

# Database connection
conn = sqlite3.connect('products.db')
c = conn.cursor()

# Create products table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS products (
             id INTEGER PRIMARY KEY,
             title TEXT NOT NULL,
             description TEXT,
             price REAL NOT NULL
             )''')
conn.commit()

# Close cursor and connection
c.close()
conn.close()

# Helper function to execute SQL query
def execute_query(query, values=()):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute(query, values)
    conn.commit()
    result = c.fetchall()
    c.close()
    conn.close()
    return result

# GET /products
@app.route('/products', methods=['GET'])
def get_products():
    products = execute_query("SELECT * FROM products")
    return jsonify(products)

# GET /products/{id}
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = execute_query("SELECT * FROM products WHERE id=?", (id,))
    if not product:
        abort(404)
    return jsonify(product[0])

# POST /products
@app.route('/products', methods=['POST'])
def create_product():
    if not request.json or 'title' not in request.json or 'price' not in request.json:
        abort(400)
    title = request.json['title']
    description = request.json.get('description', '')
    price = request.json['price']
    execute_query("INSERT INTO products (title, description, price) VALUES (?, ?, ?)", (title, description, price))
    return jsonify({'message': 'Product created successfully'}), 201

# PUT /products/{id}
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = execute_query("SELECT * FROM products WHERE id=?", (id,))
    if not product:
        abort(404)
    if not request.json:
        abort(400)
    title = request.json.get('title', product[0][1])
    description = request.json.get('description', product[0][2])
    price = request.json.get('price', product[0][3])
    execute_query("UPDATE products SET title=?, description=?, price=? WHERE id=?", (title, description, price, id))
    return jsonify({'message': 'Product updated successfully'})

# DELETE /products/{id}
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = execute_query("SELECT * FROM products WHERE id=?", (id,))
    if not product:
        abort(404)
    execute_query("DELETE FROM products WHERE id=?", (id,))
    return jsonify({'message': 'Product deleted successfully'})

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

if _name_ == '_main_':
    app.run(debug=True)