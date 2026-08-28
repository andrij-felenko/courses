from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class NodeType(Enum):
    LEAF = "LEAF"
    OR = "OR"
    AND = "AND"


@dataclass
class DreadScore:
    damage: float = 0.0
    reproducibility: float = 0.0
    exploitability: float = 0.0
    affected_users: float = 0.0
    discoverability: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.damage
            + self.reproducibility
            + self.exploitability
            + self.affected_users
            + self.discoverability
        ) / 5.0


@dataclass
class AttackNode:
    name: str
    node_type: NodeType
    cost: float = 0.0
    probability: float = 0.0
    skill_level: int = 0
    dread: DreadScore = field(default_factory=DreadScore)
    children: List["AttackNode"] = field(default_factory=list)

    def add_child(self, child: "AttackNode") -> None:
        self.children.append(child)

    def evaluate(self) -> None:
        for child in self.children:
            child.evaluate()

        if self.node_type == NodeType.LEAF or not self.children:
            return

        if self.node_type == NodeType.OR:
            self.cost = min(c.cost for c in self.children)
            prod_inv = 1.0
            for c in self.children:
                prod_inv *= (1.0 - c.probability)
            self.probability = 1.0 - prod_inv
            self.skill_level = min(c.skill_level for c in self.children)
            self.dread = max(self.children, key=lambda c: c.dread.total).dread

        elif self.node_type == NodeType.AND:
            self.cost = sum(c.cost for c in self.children)
            prod_p = 1.0
            for c in self.children:
                prod_p *= c.probability
            self.probability = prod_p
            self.skill_level = max(c.skill_level for c in self.children)

            n = len(self.children)
            self.dread = DreadScore(
                damage=sum(c.dread.damage for c in self.children) / n,
                reproducibility=sum(c.dread.reproducibility for c in self.children) / n,
                exploitability=sum(c.dread.exploitability for c in self.children) / n,
                affected_users=sum(c.dread.affected_users for c in self.children) / n,
                discoverability=sum(c.dread.discoverability for c in self.children) / n,
            )

    def print_report(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(
            f"{pad}[{self.node_type.value}] {self.name} | "
            f"Cost: {self.cost:.0f} грн | "
            f"Prob: {self.probability:.4f} ({self.probability * 100:.2f}%) | "
            f"Skill: {self.skill_level} | "
            f"DREAD: {self.dread.total:.1f}/10"
        )
        for child in self.children:
            child.print_report(indent + 1)


if __name__ == "__main__":
    root = AttackNode("Злам платіжного шлюзу", NodeType.OR)

    branch1 = AttackNode("API підробка", NodeType.AND)
    branch1.add_child(AttackNode("Фішинг API-ключа", NodeType.LEAF, cost=25000.0, probability=0.20, skill_level=2, dread=DreadScore(8, 7, 6, 9, 5)))
    branch1.add_child(AttackNode("BGP/IP spoofing", NodeType.LEAF, cost=15000.0, probability=0.30, skill_level=3, dread=DreadScore(6, 8, 5, 4, 7)))

    branch2 = AttackNode("SQL-ін'єкція", NodeType.AND)
    branch2.add_child(AttackNode("Виявлення SQLi", NodeType.LEAF, cost=10000.0, probability=0.10, skill_level=2, dread=DreadScore(9, 9, 8, 10, 6)))
    branch2.add_child(AttackNode("Обхід WAF", NodeType.LEAF, cost=20000.0, probability=0.25, skill_level=3, dread=DreadScore(7, 6, 5, 8, 4)))

    root.add_child(branch1)
    root.add_child(branch2)

    root.evaluate()
    root.print_report()
