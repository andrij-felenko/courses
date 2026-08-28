# web/routes.py — лише переклад HTTP ↔ виклик сценарію
from flask import Blueprint, request, jsonify
from application.place_order import PlaceOrder, OutOfStock, UnknownProduct

def make_routes(place: PlaceOrder) -> Blueprint:
    bp = Blueprint("orders", __name__)

    @bp.post("/orders")
    def create():
        body = request.get_json()
        try:
            result = place.run(body["items"], body.get("promo"))
        except UnknownProduct as e:
            return jsonify(error=f"немає товару {e}"), 404
        except OutOfStock as e:
            return jsonify(error=f"замало {e}"), 409
        return jsonify(result), 201

    return bp
