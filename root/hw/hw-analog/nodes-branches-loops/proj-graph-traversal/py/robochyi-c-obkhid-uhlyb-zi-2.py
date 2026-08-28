    def collect_loop(self, br: int, branches: list[Branch]) -> list[int]:
        """Зібрати фундаментальний контур хорди br: список номерів його гілок."""
        a, b = branches[br].a, branches[br].b
        loop = [br]                              # сама хорда замикає контур

        da, db = self._depth(a), self._depth(b)
        pa, pb = a, b
        # підняти глибший кінець до рівня — і зібрати пройдені ним гілки
        while da > db:
            loop.append(self.parent_br[pa])
            pa = self.parent_node[pa]
            da -= 1
        while db > da:
            loop.append(self.parent_br[pb])
            pb = self.parent_node[pb]
            db -= 1
        # далі крокуємо разом до спільного предка, збираючи гілки з обох боків
        while pa != pb:
            loop.append(self.parent_br[pa])
            pa = self.parent_node[pa]
            loop.append(self.parent_br[pb])
            pb = self.parent_node[pb]
        return loop                              # усі гілки контуру

    def _depth(self, v: int) -> int:
        """Глибина вузла v від кореня дерева."""
        d = 0
        while v != -1:
            v = self.parent_node[v]
            d += 1
        return d
