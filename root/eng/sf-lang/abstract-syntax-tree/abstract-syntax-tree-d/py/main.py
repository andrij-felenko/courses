from dataclasses import dataclass
from typing import Union

class ASTNode:
    pass

@dataclass
class NumberNode(ASTNode):
    value: float

@dataclass
class BinaryOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode
