#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    some = Pizza.query.all()
    return make_response(jsonify([s.to_dict() for s in some]), 200)

@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    return make_response(jsonify([p.to_dict() for p in pizzas]), 200)

@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    return make_response(jsonify([r.to_dict() for r in restaurants]), 200)
@app.route('/restaurants/<int:id>')
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    def map_pizzas(rp):
        object = rp.to_dict()
        object['pizza'] = rp.pizza.to_dict()
        return object
        
    if restaurant:
        object = restaurant.to_dict()
        object['restaurant_pizzas'] = [map_pizzas(rp) for rp in restaurant.restaurant_pizzas]
        return make_response(jsonify(object), 200)
    return make_response(jsonify({"error":"Restaurant not found"}), 404)
@app.route('/restaurants/<int:id>',methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({'error':'Restaurant not found'}),404)
    db.session.delete(restaurant)
    db.session.commit()
    return make_response(jsonify({}), 204)
@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizza():
    data = request.get_json()
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get('pizza_id')
    price = data.get('price')

    try:
        restauran_pizza = RestaurantPizza(pizza_id=pizza_id, restaurant_id=restaurant_id, price=price)
        db.session.add(restauran_pizza)
        db.session.commit()
        object = restauran_pizza.to_dict()
        object['restaurant']=restauran_pizza.restaurant.to_dict()
        object['pizza']=restauran_pizza.pizza.to_dict()
        return make_response(jsonify(object), 201)
    except Exception as e: 
        return make_response(jsonify({'errors':[str(e)]}),400)
if __name__ == "__main__":
    app.run(port=5555, debug=True)
