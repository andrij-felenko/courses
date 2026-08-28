import math
from dataclasses import dataclass

S       = 13          # сітка S×S
B       = 3           # якорів на клітинку
C       = 20          # класів
STRIDE  = 32          # крок сітки: вхід 416 / S(13) = 32
K       = B * 5 + C   # глибина на клітинку = 35
MAX_DET = 256         # стеля рамок після фільтра

@dataclass
class Det:
    x1: float; y1: float; x2: float; y2: float   # рамка у пікселях (кути)
    score: float                                 # підсумкова оцінка = objectness · max(class)
    cls: int                                     # індекс класу

# форми якорів у пікселях (ширина, висота) — підібрані під дані, не випадкові
ANCHOR_W = (116.0, 30.0, 60.0)
ANCHOR_H = ( 90.0, 61.0, 45.0)

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))
