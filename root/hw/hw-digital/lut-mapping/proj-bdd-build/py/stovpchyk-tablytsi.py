    def value(self, u, env):
        while u > TRUE:                                 # один шлях згори до листка
            v, lo, hi = self.node[u]
            u = hi if env[v] else lo
        return u == TRUE

    def support(self, root):
        """Змінні, яких вузол справді торкається, у порядку діаграми."""
        seen, stack, vs = set(), [root], []
        while stack:
            u = stack.pop()
            if u in seen or u <= TRUE:
                continue
            seen.add(u)
            v, lo, hi = self.node[u]
            if v not in vs:
                vs.append(v)
            stack += [lo, hi]
        return sorted(vs, key=lambda v: self.rank[v])

    def bits(self, root, vs=None):
        """Прошивка LUT: біт k = значення функції на адресі k (перша змінна — старша)."""
        vs = self.support(root) if vs is None else vs
        n = len(vs)
        word = 0
        for addr in range(1 << n):
            env = {v: (addr >> (n - 1 - k)) & 1 for k, v in enumerate(vs)}
            if self.value(root, env):
                word |= 1 << addr
        return word
