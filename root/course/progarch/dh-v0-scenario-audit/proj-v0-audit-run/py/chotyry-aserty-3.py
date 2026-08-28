import hub

def test_two_rooms_each_own_heater(monkeypatch):
    fired = {"bedroom": [], "living": []}

    # структура знає лише ОДИН давач і ОДНУ грілку — чиї вони, вона не питає
    monkeypatch.setattr(hub, "read_sensor", lambda: 18.0)                 # холодно
    monkeypatch.setattr(hub, "heater_on",  lambda: fired["bedroom"].append("on"))
    monkeypatch.setattr(hub, "heater_off", lambda: fired["bedroom"].append("off"))

    hub.step()

    # у вітальні свій давач і своя грілка — а їх у структурі просто немає
    assert fired["living"], "грілка вітальні жодного разу не отримала команди"
