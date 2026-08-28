# test_idor_access.py — перебір як вартовий регресії (pytest + FastAPI TestClient)
import pytest
from starlette.testclient import TestClient
from app import app

OWN, NEIGHBOR, ABSENT, SHARED = 4021, 4022, 999999, 4055

@pytest.fixture
def c4021():
    client = TestClient(app)
    client.cookies.set("session", login_as(4021))     # сесія мешканця #4021
    return client

def test_own_home_200(c4021):
    assert c4021.get(f"/api/homes/{OWN}/devices").status_code == 200

def test_shared_home_200(c4021):                       # упущений членом родини
    assert c4021.get(f"/api/homes/{SHARED}/devices").status_code == 200

def test_neighbor_existing_404(c4021):                 # чужий ІСНУЄ → 404, не 200, не 403
    assert c4021.get(f"/api/homes/{NEIGHBOR}/devices").status_code == 404

def test_absent_404(c4021):                            # нема зовсім → теж 404
    assert c4021.get(f"/api/homes/{ABSENT}/devices").status_code == 404

def test_sweep_leaks_nothing(c4021):                   # цілий перебір сусідів
    for home_id in range(OWN + 1, OWN + 31):
        if home_id == SHARED:
            continue
        assert c4021.get(f"/api/homes/{home_id}/devices").status_code == 404, f"home {home_id} тече"
