# tests/test_impermeable_behavior.py
import pytest
from acl.order_translator import translate_order
from domain.errors import UnsupportedByModel
from domain.order import Order
from crm.dto import CrmOrderDto

def good(**over) -> CrmOrderDto:
    base = dict(sku="ART-00417/RED/XL", qty=5,
                status_code=2, client_ref="CL:88213")
    base.update(over)
    return CrmOrderDto(**base)

def test_valid_order_translates_to_clean_order():
    order = translate_order(good())
    assert isinstance(order, Order)
    assert order.quantity == 5
    assert order.product.article.code == "ART-00417"
    assert order.client.value == "88213"          # "CL:" зрізано

# Кожне чуже поняття без пари МУСИТЬ відбитися UnsupportedByModel.
@pytest.mark.parametrize("name, dto", [
    ("повернення",        good(qty=-3)),
    ("нульова кількість", good(qty=0)),
    ("невідомий статус",  good(status_code=7)),
    ("кривий SKU",        good(sku="ART-00417-RED")),
    ("client без CL:",    good(client_ref="88213")),
])
def test_rejects_unsupported(name, dto):
    with pytest.raises(UnsupportedByModel):
        translate_order(dto)
