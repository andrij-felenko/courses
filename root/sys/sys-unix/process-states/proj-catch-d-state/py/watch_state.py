#!/usr/bin/env python3
"""watch_state.py <pid> [період_мс] — смуга станів і час у кожному стані."""
import os, signal, sys, time


def state_of(pid):
    with open(f"/proc/{pid}/stat", "rb") as f:
        raw = f.read()
    # ім'я програми — в дужках і може містити ')': ріжемо по ОСТАННІЙ
    return raw[raw.rindex(b")") + 2:].split(b" ", 1)[0].decode()


def wchan_of(pid):
    try:
        with open(f"/proc/{pid}/wchan") as f:
            return f.read().strip() or "0"
    except OSError:
        return "0"


def main():
    pid = int(sys.argv[1])
    nap = (float(sys.argv[2]) if len(sys.argv) > 2 else 50) / 1000
    band, dwell = [], {}
    prev = prev_t = None
    cont_sent = False
    t0 = time.monotonic()

    while True:
        try:
            st = state_of(pid)
        except (OSError, ValueError):
            break
        t = time.monotonic() - t0

        if st != prev:
            if prev is not None:
                dwell[prev] = dwell.get(prev, 0.0) + (t - prev_t)
            print(f"{t:7.3f}  {st}   wchan={wchan_of(pid)}")
            prev, prev_t = st, t
        band.append(st)

        if st == "T" and not cont_sent and t - prev_t > 2.0:
            os.kill(pid, signal.SIGCONT)
            cont_sent = True
            print(f"{t:7.3f}  →   надіслано SIGCONT")

        time.sleep(nap)

    total = time.monotonic() - t0
    if prev is not None:
        dwell[prev] = dwell.get(prev, 0.0) + (total - prev_t)

    print("\nсмуга:", "".join(band))
    for st, sec in sorted(dwell.items(), key=lambda kv: -kv[1]):
        print(f"  {st}: {sec:6.2f} c   ({100 * sec / total:4.1f} %)")


main()
