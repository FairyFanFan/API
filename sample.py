from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapi.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.Float, nullable=False)

    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price

# Define the Product schema for serialization
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a new product
@app.route('/products', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    
    new_product = Product(name, description, price)

    try:
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding product"}), 400

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = products_schema.dump(products)
    return jsonify({"products": result})

# Get a single product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return product_schema.jsonify(product)

# Run the app
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
