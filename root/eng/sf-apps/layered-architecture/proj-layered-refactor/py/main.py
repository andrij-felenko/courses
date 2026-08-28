# main.py — ЄДИНЕ місце, де конкретні класи названо на ім'я
import sqlite3
from flask import Flask
from infra.sql_repos import SqlProductRepo, SqlOrderRepo
from application.place_order import PlaceOrder
from web.routes import make_routes

def build_app() -> Flask:
    conn = sqlite3.connect("shop.db", check_same_thread=False)
    products = SqlProductRepo(conn)          # обіцянку виконує SQL —
    orders = SqlOrderRepo(conn)              #   але знає про це лише тут
    place = PlaceOrder(products, orders)     # сценарію дали готові сховища
    app = Flask(__name__)
    app.register_blueprint(make_routes(place))
    return app

app = build_app()
