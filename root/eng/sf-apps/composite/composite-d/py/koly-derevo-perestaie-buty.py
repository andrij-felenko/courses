class Composite(Component):
    def add(self, child: Component) -> None:
        if child is self or self._has_ancestor(child):
            raise ValueError("додавання створило б цикл")   # гучна відмова
        if child.parent is not None:
            child.parent.remove(child)
        self.children.append(child)
        child.parent = self

    def _has_ancestor(self, candidate: Component) -> bool:
        p = self.parent
        while p is not None:                 # ідемо від себе вгору до кореня
            if p is candidate:
                return True
            p = p.parent
        return p is not None                 # (недосяжно: цикл вище вже неможливий)
