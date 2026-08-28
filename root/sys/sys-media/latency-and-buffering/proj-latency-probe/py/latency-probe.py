#!/usr/bin/env python3
"""latency-probe.py — вік буфера в кількох точках живого конвеєра.

    python3 latency-probe.py "<опис конвеєра>" елемент:пад [елемент:пад ...]

Прототип: тримає ковзне вікно останніх вимірів замість гістограми —
коротше й показує свіжу поведінку, а не всю історію.
"""
import sys
import threading
from collections import deque

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

WARMUP = 2 * Gst.SECOND
WINDOW = 3000


class Point:
    def __init__(self, label):
        self.label = label
        self.segment = None                  # чіпає лише потік цього пада
        self.ages = deque(maxlen=WINDOW)     # мс, під замком
        self.n = 0
        self.late = 0

    def quantile(self, q):
        w = sorted(self.ages)
        return w[min(int(q * len(w)), len(w) - 1)] if w else None


class Probe:
    def __init__(self, desc, specs):
        self.pipeline = Gst.parse_launch(desc)
        self.lock = threading.Lock()
        self.live, self.contract, self.ceiling = False, None, None
        self.points = []
        for spec in specs:
            name, _, padname = spec.partition(":")
            el = self.pipeline.get_by_name(name)
            if el is None:
                sys.exit(f"немає елемента «{name}» — дайте йому name= в описі")
            pad = el.get_static_pad(padname)
            if pad is None:
                sys.exit(f"в елемента «{name}» немає пада «{padname}»")
            pt = Point(spec)
            pad.add_probe(
                Gst.PadProbeType.BUFFER | Gst.PadProbeType.EVENT_DOWNSTREAM,
                self._on_pad, pt)
            self.points.append(pt)

    # ── що конвеєр пообіцяв
    def read_contract(self):
        q = Gst.Query.new_latency()
        if not self.pipeline.query(q):
            return
        live, mn, mx = q.parse_latency()
        with self.lock:
            self.live = live
            self.contract = None if mn == Gst.CLOCK_TIME_NONE else mn
            self.ceiling = None if mx == Gst.CLOCK_TIME_NONE else mx

    # ── що вийшло насправді
    def _on_pad(self, pad, info, pt):
        if info.type & Gst.PadProbeType.EVENT_DOWNSTREAM:
            ev = info.get_event()
            if ev.type == Gst.EventType.SEGMENT:
                pt.segment = ev.parse_segment()
            return Gst.PadProbeReturn.OK

        buf = info.get_buffer()
        if pt.segment is None or buf.pts == Gst.CLOCK_TIME_NONE:
            return Gst.PadProbeReturn.OK

        rt_buf = pt.segment.to_running_time(Gst.Format.TIME, buf.pts)
        now = self.pipeline.get_current_running_time()   # годинник − base_time
        if rt_buf == Gst.CLOCK_TIME_NONE or now == Gst.CLOCK_TIME_NONE:
            return Gst.PadProbeReturn.OK
        if now < rt_buf or now < WARMUP:      # не живе джерело або розігрів
            return Gst.PadProbeReturn.OK

        age = now - rt_buf
        with self.lock:
            pt.ages.append(age // Gst.MSECOND)
            pt.n += 1
            if self.contract is not None and age > self.contract:
                pt.late += 1
        return Gst.PadProbeReturn.OK

    # ── звіт раз на дві секунди
    def report(self):
        self.read_contract()
        with self.lock:
            budget = None if self.contract is None else self.contract / Gst.MSECOND
            if budget is None:
                print("\nконтракт: ще невідомий")
            else:
                live = "так" if self.live else "ні"
                print(f"\nконтракт: live={live}  min={budget:.1f} мс")
            print(f"{'точка':<24} {'n':>7} {'p50':>8} {'p95':>8} "
                  f"{'макс':>8} {'приріст':>9}")

            prev = 0
            for pt in self.points:
                p50, p95 = pt.quantile(0.50), pt.quantile(0.95)
                if p50 is None:
                    print(f"{pt.label:<24} {'—':>7}")
                    continue
                print(f"{pt.label:<24} {pt.n:>7} {p50:>8.0f} {p95:>8.0f} "
                      f"{max(pt.ages):>8.0f} {p50 - prev:>+9.0f}")
                prev = p50

            last = self.points[-1]
            if budget is not None and last.n:
                print(f"   запас до дедлайну: p50 {budget - last.quantile(0.50):+.0f} мс,"
                      f" p95 {budget - last.quantile(0.95):+.0f} мс;"
                      f" після дедлайну {last.late} з {last.n}")
        return True                          # таймер лишається жити

    # ── шина
    def on_bus(self, bus, msg):
        if msg.type == Gst.MessageType.LATENCY:
            self.pipeline.recalculate_latency()   # інакше контракт застаріє
            self.read_contract()
        elif msg.type == Gst.MessageType.STATE_CHANGED and msg.src == self.pipeline:
            if msg.parse_state_changed()[1] == Gst.State.PLAYING:
                self.read_contract()              # аж тепер є base_time
        elif msg.type == Gst.MessageType.ERROR:
            print(msg.parse_error()[0].message, file=sys.stderr)
            self.loop.quit()
        elif msg.type == Gst.MessageType.EOS:
            self.loop.quit()
        return True

    def run(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_bus)
        self.loop = GLib.MainLoop()
        GLib.timeout_add_seconds(2, self.report)
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            self.loop.run()
        finally:
            self.pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    Gst.init(None)
    if len(sys.argv) < 3:
        sys.exit('вжиток: latency-probe.py "<опис конвеєра>" елемент:пад ...')
    Probe(sys.argv[1], sys.argv[2:]).run()
