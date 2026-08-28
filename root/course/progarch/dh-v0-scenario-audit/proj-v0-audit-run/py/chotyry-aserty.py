import socket
import time
import hub

def test_offline_still_decides(monkeypatch):
    # середовище: інтернету НЕМА — будь-який сокет одразу падає
    def no_network(*a, **k):
        raise OSError("мережу відрубано")
    monkeypatch.setattr(socket, "socket", no_network)

    # давач каже «холодно»; команди грілці лише записуємо
    monkeypatch.setattr(hub, "read_sensor", lambda: 18.0)
    fired = []
    monkeypatch.setattr(hub, "heater_on",  lambda: fired.append("on"))
    monkeypatch.setattr(hub, "heater_off", lambda: fired.append("off"))

    hub.step()                                  # один крок рішення

    assert fired == ["on"]                       # рішення сталося попри вбиту мережу
