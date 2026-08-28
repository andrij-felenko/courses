class Composite(Component):
    def __init__(self):
        super().__init__()
        self.children: list[Component] = []
        self._cached: int | None = None      # None = брудний

    def size(self) -> int:
        if self._cached is None:             # брудний — рахуємо й кешуємо
            self._cached = sum(c.size() for c in self.children)
        return self._cached                  # чистий — миттєво

    def invalidate(self) -> None:            # себе й усіх пращурів — у брудні
        p: "Composite | None" = self
        while p is not None:
            if p._cached is None:            # уже брудний вище → далі не йдемо
                break
            p._cached = None
            p = p.parent

    def add(self, child: Component) -> None:
        self.children.append(child)
        child.parent = self
        self.invalidate()                    # шлях до кореня тепер брудний
