    def var(self, v):
        return self.make_node(v, FALSE, TRUE)

    def apply(self, op, u, v):
        key = (op, u, v)
        got = self.computed.get(key)                    # таблиця обчисленого
        if got is not None:
            return got
        if u <= TRUE and v <= TRUE:                     # обидва — термінали: рахуємо
            return {"and": u & v, "or": u | v, "xor": u ^ v}[op]
        top = len(self.order)                           # ранг «нижче за все»
        ru = self.rank[self.node[u][0]] if u > TRUE else top
        rv = self.rank[self.node[v][0]] if v > TRUE else top
        r = min(ru, rv)                                 # старша зі змінних двох вершин
        ulo, uhi = (self.node[u][1], self.node[u][2]) if ru == r else (u, u)
        vlo, vhi = (self.node[v][1], self.node[v][2]) if rv == r else (v, v)
        res = self.make_node(self.order[r],
                             self.apply(op, ulo, vlo),
                             self.apply(op, uhi, vhi))
        self.computed[key] = res
        return res
