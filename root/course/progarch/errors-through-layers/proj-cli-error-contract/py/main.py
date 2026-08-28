#!/usr/bin/env python3
"""dh-temp — CLI над хабом Digital Homes: прочитати температуру кімнати.
Результат → stdout · діагностика → stderr · рід результату → код виходу."""
import sys, json, argparse
from hub import read_temp, SensorUnavailable      # той самий read_temp зі статті

EX_OK       = 0     # температура в stdout
EX_USAGE    = 2     # погана команда: нема / невідома кімната
EX_SENSOR   = 3     # давач недоступний — збій світу, можна повторити
EX_INTERNAL = 70    # внутрішній баг (EX_SOFTWARE із sysexits) — не мало статися

KNOWN_ROOMS = ("вітальня", "спальня", "кухня")

def fail(args, code, kind, human):
    """Єдиний вихід через збій: людині — рядок у stderr, машині — json у stderr."""
    if args.json:
        json.dump({"error": kind, "room": args.room, "message": human},
                  sys.stderr, ensure_ascii=False)
        sys.stderr.write("\n")
    else:
        print(f"dh-temp: {human}", file=sys.stderr)   # діагностика — у stderr, не в stdout
    sys.exit(code)

def run(args):
    if args.room not in KNOWN_ROOMS:                  # ВХІД з краю — недовірений, перевіряємо тут
        fail(args, EX_USAGE, "unknown-room",
             f"немає кімнати «{args.room}»; відомі: {', '.join(KNOWN_ROOMS)}")
    try:
        t = read_temp(args.room)                      # може кинути SensorUnavailable
    except SensorUnavailable as e:                    # очікуване, операційне → перекладаємо в код
        fail(args, EX_SENSOR, "sensor-unavailable", str(e))
    # РЕЗУЛЬТАТ — і тільки він — у stdout:
    if args.json:
        print(json.dumps({"room": args.room, "temp_c": round(t, 1)}, ensure_ascii=False))
    else:
        print(f"{t:.1f}")
    return EX_OK

def main(argv):
    p = argparse.ArgumentParser(prog="dh-temp")
    p.add_argument("room")
    p.add_argument("--json", action="store_true")
    return run(p.parse_args(argv))                     # погана опція → argparse сам: stderr + вихід 2

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise                                          # наші свідомі виходи (0/2/3) — пропустити
    except Exception:                                  # сюди доходить ЛИШЕ несподіване = баг
        import traceback
        traceback.print_exc()                          # трейсбек у stderr — це ЛОГ дефекту
        sys.exit(EX_INTERNAL)                          # але тег — 70, не сирий 1
