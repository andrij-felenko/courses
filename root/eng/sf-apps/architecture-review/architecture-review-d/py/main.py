# Сценарій, що пройшов рев'ю, стає стоячою фітнес-функцією:
# «шлях аварійного стопу НЕ залежить від черги телеметрії».
# Порушиш межу — впаде CI, а не поле через пів року.
from arch import module_graph

STOP = "control/estop"
TELEMETRY_QUEUE = "telemetry/queue"

def test_estop_not_through_telemetry_queue():
    reachable = module_graph.dependencies_of(STOP)  # усі транзитивні залежності
    assert TELEMETRY_QUEUE not in reachable
