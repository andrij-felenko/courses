import inspect

class Container:
    def __init__(self):
        self._bindings = {}      # обіцянка → реалізація
        self._cache = {}         # обіцянка → готовий одинак
        self._building = []       # стек тих, хто ЗАРАЗ будується (для лову циклів)

    def bind(self, promise, impl):
        self._bindings[promise] = impl
        return self

    def resolve(self, promise):
        # кеш: уже зібраний одинак — віддати, не будувати вдруге
        if promise in self._cache:
            return self._cache[promise]

        # цикл: цей тип уже будується вище по стеку — ми повернулися по кільцю
        if promise in self._building:
            chain = " → ".join(t.__name__ for t in self._building) + f" → {promise.__name__}"
            raise RuntimeError(f"Циклічна залежність: {chain}")

        self._building.append(promise)       # поклали на стек: почали будувати
        try:
            impl = self._bindings.get(promise, promise)
            sig = inspect.signature(impl.__init__)
            params = [p for name, p in sig.parameters.items() if name != "self"]
            args = [self.resolve(p.annotation) for p in params]   # ← рекурсія: обхід графа
            obj = impl(*args)
        finally:
            self._building.pop()             # зняли зі стека хоч би що (навіть на помилці)

        self._cache[promise] = obj           # запам'ятали одинак
        return obj
