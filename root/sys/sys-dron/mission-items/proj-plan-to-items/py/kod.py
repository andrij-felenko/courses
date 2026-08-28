"""Складання плаского списку записів місії з файлу .plan."""
import json
import math
from dataclasses import dataclass, field

MAV_FRAME_GLOBAL     = 0
MAV_FRAME_MISSION    = 2
MAV_CMD_NAV_WAYPOINT = 16
MAV_CMD_DO_JUMP      = 177


class PlanError(Exception):
    """Файл прочитано, але зібрати з нього місію не можна."""


@dataclass
class Record:
    """Один запис місії: ті самі поля, що в MISSION_ITEM_INT, плюс ім'я з файлу."""
    command:      int
    frame:        int
    params:       list          # param1..4, x, y, z — координати в ГРАДУСАХ
    autocontinue: int = 1
    do_jump_id:   int = -1      # -1 = імені немає
    seq:          int = 0       # проставить перенумерація
    current:      int = 0


def _number(value):
    """NaN у файлі записано як null: JSON не має способу зобразити NaN числом."""
    return math.nan if value is None else float(value)


def _seven_params(obj):
    """Старіша форма елемента клала в params лише param1..param4, а координату —
    окремим ключем coordinate: [широта, довгота, висота]. Зводимо до теперішньої
    форми, інакше спіткнемося на першому ж елементі старого файлу."""
    params = list(obj["params"])

    if len(params) == 4 and "coordinate" in obj:
        coordinate = obj["coordinate"]
        if len(coordinate) != 3:
            raise PlanError("ключ coordinate має бути [широта, довгота, висота]")
        params += list(coordinate)

    if len(params) != 7:
        raise PlanError(f"очікується рівно 7 параметрів, знайдено {len(params)}")
    return params


def _record_from_simple_item(obj):
    return Record(
        command      = int(obj["command"]),
        frame        = int(obj["frame"]),
        params       = [_number(p) for p in _seven_params(obj)],
        autocontinue = 1 if obj.get("autoContinue", True) else 0,
        do_jump_id   = int(obj.get("doJumpId", -1)),
    )


def records_from_plan(plan, home_as_item_zero):
    """Проходи 1 і 2: читання масиву items і — за потреби — дім нульовим записом."""
    mission = plan["mission"]
    items = mission["items"]
    if not items:
        raise PlanError("масив items порожній: порожня місія і відсутня місія — різні речі")

    records = []

    if home_as_item_zero:
        home = mission["plannedHomePosition"]
        if len(home) != 3:
            raise PlanError("plannedHomePosition має бути [широта, довгота, висота AMSL]")
        records.append(Record(
            command = MAV_CMD_NAV_WAYPOINT,
            frame   = MAV_FRAME_GLOBAL,          # дім завжди в абсолютній висоті
            params  = [0.0, 0.0, 0.0, 0.0,
                       float(home[0]), float(home[1]), float(home[2])],
        ))

    for i, obj in enumerate(items):
        kind = obj.get("type")
        if kind == "SimpleItem":
            try:
                records.append(_record_from_simple_item(obj))
            except (PlanError, KeyError, TypeError) as exc:
                raise PlanError(f"items[{i}]: {exc}") from exc
        elif kind == "ComplexItem":
            raise PlanError(
                f"items[{i}]: складений елемент «{obj.get('complexItemType')}» "
                "зберігається параметрами й розгортається не тут")
        else:
            raise PlanError(f"items[{i}]: невідомий тип елемента «{kind}»")

    return records
