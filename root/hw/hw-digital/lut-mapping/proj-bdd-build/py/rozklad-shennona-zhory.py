    def build(self, fn):
        """fn(env) -> bool, де env — словник {змінна: 0|1}."""
        def rec(i, env):
            if i == len(self.order):
                return TRUE if fn(env) else FALSE       # дно: одне значення функції
            v = self.order[i]
            env[v] = 0
            lo = rec(i + 1, env)                        # кофактор при v = 0
            env[v] = 1
            hi = rec(i + 1, env)                        # кофактор при v = 1
            del env[v]
            return self.make_node(v, lo, hi)            # обидва правила — тут
        return rec(0, {})
