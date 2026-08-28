# -*- coding: utf-8 -*-
"""plan_flat.py — той самий розбір коротко: чим саме стане .plan на дроті."""
import json, math, sys

NAV_WAYPOINT, DO_JUMP, FRAME_GLOBAL = 16, 177, 0

NAMES = {16: "NAV_WAYPOINT", 20: "NAV_RETURN_TO_LAUNCH", 21: "NAV_LAND",
         22: "NAV_TAKEOFF", 177: "DO_JUMP", 178: "DO_CHANGE_SPEED",
         206: "DO_SET_CAM_TRIGG_DIST"}


def num(value):
    return math.nan if value is None else float(value)      # null у файлі — це NaN


def one(obj, origin):
    params = obj["params"]
    if len(params) != 7:
        raise ValueError("елемент має %d параметрів замість семи" % len(params))
    return dict(seq=0, command=obj["command"], frame=obj["frame"],
                p=[num(x) for x in params], origin=origin)


def flatten(mission):
    lat, lon, alt = (num(x) for x in mission["plannedHomePosition"])
    flat = [dict(seq=0, command=NAV_WAYPOINT, frame=FRAME_GLOBAL,
                 p=[0, 0, 0, 0, lat, lon, alt], origin="plannedHomePosition")]
    seq_of_id = {}

    for obj in mission["items"]:
        if obj["type"] == "SimpleItem":
            if "doJumpId" in obj:
                seq_of_id[obj["doJumpId"]] = len(flat)
            flat.append(one(obj, "SimpleItem"))
        elif obj["type"] == "ComplexItem":
            kind = obj["complexItemType"]
            inner = obj.get("TransectStyleComplexItem", {})
            if "Items" not in inner:
                raise ValueError("складений «%s» не тримає у файлі готових команд" % kind)
            flat += [one(sub, kind) for sub in inner["Items"]]
        else:
            raise ValueError("невідомий тип елемента: %s" % obj["type"])

    for seq, item in enumerate(flat):
        item["seq"] = seq
    for item in flat:
        if item["command"] == DO_JUMP:
            target = int(item["p"][0])
            if target not in seq_of_id:
                raise ValueError("DO_JUMP веде на doJumpId %d, якого в плані немає" % target)
            item["p"][0] = seq_of_id[target]
    return flat


def drop_home(flat):
    del flat[0]
    for item in flat:
        item["seq"] -= 1
        if item["command"] == DO_JUMP:
            item["p"][0] -= 1


def show(flat, title):
    print(title)
    print("seq  команда                frame     p1     широта    довгота  висота  джерело")
    for it in flat:
        print("%3d  %-22s %5d %6.0f  %9.4f  %9.4f  %6.1f  %s" % (
            it["seq"], NAMES.get(it["command"], "?"), it["frame"],
            it["p"][0], it["p"][4], it["p"][5], it["p"][6], it["origin"]))
    print()


plan = json.load(open(sys.argv[1], encoding="utf-8"))
flat = flatten(plan["mission"])
show(flat, "ArduPilot: домашня точка лишається номером 0")
drop_home(flat)
show(flat, "PX4: домашньої точки на дроті немає, решта зсунулася на одиницю")
