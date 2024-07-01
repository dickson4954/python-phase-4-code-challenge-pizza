#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, make_response,request
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db,render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def restaurants():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        }
        restaurants.append(restaurant_dict)
    return jsonify(restaurants), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
    if restaurant:
        restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': restaurant_pizza.id,
                    'restaurant_id': restaurant_pizza.restaurant_id,
                    'pizza_id': restaurant_pizza.pizza_id,
                    'price': restaurant_pizza.price,
                    'pizza': {
                        'id': restaurant_pizza.pizza.id,
                        'name': restaurant_pizza.pizza.name,
                        'ingredients': restaurant_pizza.pizza.ingredients
                    }
                } for restaurant_pizza in restaurant.restaurant_pizzas
            ]
        }
        response =make_response(
            jsonify(restaurant_dict),
         200
         )
        return response
    else:
        response=make_response(
            jsonify({'error': 'Restaurant not found'}),
            404
        )
        return response
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    
    pizza_list = []
    for pizza in pizzas:
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        pizza_list.append(pizza_dict)
    
    return jsonify(pizza_list)        
@app.route('/restaurant_pizzas',methods=['POST'])
def add_pizza_post():
    if request.method == 'POST':
       try:
            restaurant_pizza= RestaurantPizza(
                 price = request.get_json()["price"],
                 restaurant_id= request.get_json()["restaurant_id"],
                 pizza_id= request.get_json()["pizza_id"]
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            response= make_response(restaurant_pizza.to_dict(),201,{"content-type":"application/json"})
            return response
       except ValueError as e:
        message = {"errors": ["validation errors"]}
        response = make_response(message, 400)
        return response
            
@app.route('/restaurants/<int:id>',methods=['DELETE'])
def del_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
       RestaurantPizza.query.filter_by(restaurant_id=id).delete()
       db.session.delete(restaurant)
       db.session.commit()
       response= make_response(
             jsonify({'message': 'Restaurant is deleted successfully'}),
             204
            )
       return response
    else:
        response= make_response(
             jsonify({'message': 'Restaurant is not found'}),
             404
            )
        return response
       
            
if __name__ == "__main__":
    app.run(port=5555, debug=True)
