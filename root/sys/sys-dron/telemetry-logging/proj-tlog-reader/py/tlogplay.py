#!/usr/bin/env python3
"""tlogplay.py — читач логу телеметрії .tlog: тривалість, перемотування, темп."""
import argparse
import bisect
import sys
import time

from pymavlink.dialects.v20 import common as mav2

STAMP         = 8
USEC          = 1_000_000
INDEX_STEP    = 1 * USEC              # крок таблиці «час → зсув»
PROBE_RECORDS = 64                    # на скількох мітках вирішуємо порядок байтів
RESYNC_LIMIT  = 1 << 16               # стеля скану межі кадру, байтів
BATCH_WINDOW  = 0.003                 # с: ближче за це — однією пачкою
STAMP_FLOOR   = 1_104_537_600 * USEC  # 2005-01-01


def frame_length(hdr):
    """Довжина кадру за трьома першими байтами; None — це не кадр."""
    if hdr[0] == 0xFD:                                    # MAVLink 2
        return 12 + hdr[1] + (13 if hdr[2] & 0x01 else 0)
    if hdr[0] == 0xFE:                                    # MAVLink 1
        return 8 + hdr[1]
    return None


class Tlog:
    def __init__(self, path):
        self.f = open(path, "rb")
        self.swapped = False
        self.index = []                # [(t_usec, offset)], зростає за часом
        self.first = self.last = 0
        self.back_steps = self.breaks = 0
        self.truncated = False
        self.pending_t = None
        self._scan()
        self.position_at(0)

    # ── мітка ───────────────────────────────────────────────────────────────
    def _decode(self, raw):
        # прочитати ті самі байти як little-endian — і є перевертання
        return int.from_bytes(raw, "little" if self.swapped else "big")

    def _decide(self, head):
        ceil_usec = int(time.time() + 365 * 86400) * USEC

        def score(swapped):
            s, prev = 0, None
            for raw, _ in head:
                t = int.from_bytes(raw, "little" if swapped else "big")
                s += 1 if STAMP_FLOOR <= t <= ceil_usec else -1
                if prev is not None:
                    s += 1 if t >= prev else -1
                prev = t
            return s

        self.swapped = score(True) > score(False)   # рівність → старший-перший

    # ── прохід відкриття: тривалість, індекс, діагностика ───────────────────
    def _scan(self):
        self.f.seek(0)
        head, decided = [], False
        next_index = prev = None

        def accept(raw, off):
            nonlocal next_index, prev
            t = self._decode(raw)
            if next_index is None:
                self.first, next_index = t, t
            elif t < prev:
                self.back_steps += 1
            prev = self.last = t
            if t >= next_index:
                self.index.append((t, off))
                next_index = t + INDEX_STEP

        while True:
            off = self.f.tell()
            raw = self.f.read(STAMP)
            if len(raw) < STAMP:                    # охайний кінець файлу
                break

            hdr = self.f.read(3)
            if len(hdr) < 3:
                self.truncated = True
                break
            flen = frame_length(hdr)
            if flen is None:                        # ланцюг зірвався
                rec = self.resync_from(off + 1)
                if rec is None:
                    self.truncated = True
                    break
                self.breaks += 1
                self.f.seek(rec)
                continue
            if len(self.f.read(flen - 3)) < flen - 3:
                self.truncated = True
                break

            if decided:
                accept(raw, off)
            else:
                head.append((raw, off))
                if len(head) == PROBE_RECORDS:
                    self._decide(head)
                    decided = True
                    for r, o in head:
                        accept(r, o)

        if not decided:                             # файл коротший за пробу
            self._decide(head)
            for r, o in head:
                accept(r, o)

    # ── ресинхронізація: тут довіряти заголовкові не можна ──────────────────
    def resync_from(self, offset):
        """Найближчий після offset справжній початок ЗАПИСУ, або None."""
        self.f.seek(offset)
        mav = mav2.MAVLink(None)        # свіжий автомат = порожній стан каналу
        mav.robust_parsing = True       # сміття → BAD_DATA замість винятку

        scanned = 0
        while scanned < RESYNC_LIMIT:
            chunk = self.f.read(4096)
            if not chunk:
                return None
            scanned += len(chunk)
            for i, b in enumerate(chunk):
                msg = mav.parse_char(bytes([b]))
                if msg is None or msg.get_type() == "BAD_DATA":
                    continue
                frame_end = self.f.tell() - (len(chunk) - i - 1)
                rec = frame_end - len(msg.get_msgbuf()) - STAMP
                return rec if rec >= 0 else None
        return None

    # ── послідовне читання: кадр і одразу наступні вісім байтів ─────────────
    def position_at(self, offset):
        self.f.seek(offset)
        raw = self.f.read(STAMP)
        self.pending_t = self._decode(raw) if len(raw) == STAMP else None
        return self.pending_t is not None

    def next(self):
        """(t_usec, frame) поточного запису; далі стаємо на наступний."""
        if self.pending_t is None:
            return None
        t = self.pending_t

        hdr = self.f.read(3)
        flen = frame_length(hdr) if len(hdr) == 3 else None
        if flen is None:
            self.pending_t, self.truncated = None, True
            return None
        rest = self.f.read(flen - 3)
        if len(rest) < flen - 3:
            self.pending_t, self.truncated = None, True
            return None

        raw = self.f.read(STAMP)                    # мітка НАСТУПНОГО запису
        self.pending_t = self._decode(raw) if len(raw) == STAMP else None
        return t, hdr + rest

    # ── перемотування ──────────────────────────────────────────────────────
    def seek_to_time(self, t_usec):
        if not self.index:
            return False
        i = max(bisect.bisect_right(self.index, (t_usec, 1 << 62)) - 1, 0)
        self.position_at(self.index[i][1])
        while self.pending_t is not None and self.pending_t < t_usec:
            if self.next() is None:
                break
        return True

    def duration(self):
        return self.last - self.first if self.last > self.first else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--seek", type=float, default=0.0, help="відсоток тривалости")
    ap.add_argument("--speed", type=float, default=1.0)
    a = ap.parse_args()

    log = Tlog(a.file)
    dur = log.duration()
    print("тривалість %.3f с · стрибків часу назад %d · розривів %d%s"
          % (dur / 1e6, log.back_steps, log.breaks,
             " · хвіст обірваний" if log.truncated else ""), file=sys.stderr)

    if a.seek > 0:
        if dur == 0:
            print("нульова тривалість: перемотувати нема куди", file=sys.stderr)
        else:
            log.seek_to_time(log.first + int(dur * a.seek / 100.0))

    anchor_log = log.pending_t
    if anchor_log is None:
        return
    anchor_tick = time.monotonic()          # МОНОТОННИЙ: міряємо проміжок

    out = sys.stdout.buffer
    while log.pending_t is not None:
        # цілі в Python довільної точности й знакові — пастки з 2⁶⁴ тут немає
        ahead = log.pending_t - anchor_log
        wait = (anchor_tick + ahead / 1e6 / a.speed) - time.monotonic()
        if wait >= BATCH_WINDOW:
            time.sleep(wait)
            continue
        rec = log.next()
        if rec is None:
            break
        out.write(rec[1])
    out.flush()


if __name__ == "__main__":
    main()
