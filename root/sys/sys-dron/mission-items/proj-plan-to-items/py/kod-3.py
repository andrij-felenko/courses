INT32_MIN, INT32_MAX = -2**31, 2**31 - 1


def _pack_int32(value, field):
    """Ціле поле не має NaN і не має «майже нуля» — або число, або відмова."""
    if math.isnan(value):
        raise PlanError(f"поле {field} не може бути NaN: воно ціле, "
                        "а нулем підміняти не можна")
    if not math.isfinite(value):
        raise PlanError(f"поле {field} не є скінченним числом")
    scaled = round(value)
    if not INT32_MIN <= scaled <= INT32_MAX:
        raise PlanError(f"поле {field} ({scaled}) не влазить у int32")
    return scaled


def to_mission_item_int(rec):
    """Прохід 5: градуси → десятимільйонні частки, крім MAV_FRAME_MISSION."""
    spatial = rec.frame != MAV_FRAME_MISSION
    return {
        "seq":          rec.seq,
        "frame":        rec.frame,
        "command":      rec.command,
        "current":      rec.current,
        "autocontinue": rec.autocontinue,
        # Ці п'ять — float: NaN тут легальний і значущий («лиши як є»).
        "param1": rec.params[0],
        "param2": rec.params[1],
        "param3": rec.params[2],
        "param4": rec.params[3],
        "x": _pack_int32(rec.params[4] * 1e7 if spatial else rec.params[4], "x"),
        "y": _pack_int32(rec.params[5] * 1e7 if spatial else rec.params[5], "y"),
        "z": rec.params[6],
    }


def mission_from_plan_file(path, home_as_item_zero):
    """Увесь конвеєр в одному місці."""
    with open(path, encoding="utf-8") as handle:
        plan = json.load(handle)

    if plan.get("fileType") != "Plan":
        raise PlanError("це не файл плану: ключ fileType не «Plan»")

    records = records_from_plan(plan, home_as_item_zero)   # проходи 1 і 2
    renumber(records)                                      # прохід 3
    retarget_jumps(records)                                # прохід 4
    return [to_mission_item_int(rec) for rec in records]   # прохід 5
