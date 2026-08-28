from collections import namedtuple, defaultdict

Pin = namedtuple("Pin", "part pad")           # напр. Pin("U3", 12)

# Ланцюг = ім'я + усі піни, що мусять стати однією міддю.
# Нетлист — мапа ім'я→[піни]; це РЕАЛЬНИЙ опис плати, вектор у ній уже не фігурує.
def new_netlist():
    return defaultdict(list)

# Завести шину у нетлист: розгорнути й приписати кожному членові його пін.
# pins — піни приймача в ТОМУ Ж порядку, що й члени шини.
def attach_bus(net, bn, pins):
    for name, pin in zip(expand(bn), pins):   # zip обрізає до коротшого — як i<both
        net[name].append(pin)                 # D3 → [U3.pad], D2 → [...], …
