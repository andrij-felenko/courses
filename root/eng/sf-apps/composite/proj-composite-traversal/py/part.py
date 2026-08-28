from __future__ import annotations
from dataclasses import dataclass, field


class Component:
    name: str


@dataclass
class File(Component):
    name: str
    num_bytes: int


@dataclass
class Folder(Component):
    name: str
    children: list[Component] = field(default_factory=list)

    def add(self, c: Component) -> "Folder":
        self.children.append(c)
        return self                    # зручно ланцюжком будувати дерево


# піддослідне дерево
tree = Folder("проєкт", [
    Folder("src", [
        File("main.ts", 1200),
        File("util.ts", 800),
        Folder("ui", [
            File("button.ts", 640),
            File("modal.ts", 1500),
        ]),
    ]),
    Folder("docs", [
        File("guide.md", 300),
        File("api.md", 950),
    ]),
    File("README.md", 200),
])
