import copy

class SqlCommand:
    def __init__(self, sql: str, params: list):
        self.sql = sql
        self.params = params

proto = SqlCommand("INSERT INTO users(name) VALUES (%s)", [])

a = copy.copy(proto)        # поверхнева: params — той самий список
b = copy.copy(proto)
a.params.append("Ann")
print(b.params)             # ['Ann']  ← спільний список
print(proto.params)         # ['Ann']  ← і сам взірець забруднено

clean = SqlCommand("INSERT INTO users(name) VALUES (%s)", [])
c = copy.deepcopy(clean)    # глибока: власний список
d = copy.deepcopy(clean)
c.params.append("Bob")
print(d.params)             # []  ← незалежні, як і має бути
