"""Фаза 2: вичитка списку параметрів із закриттям дірок від втрачених кадрів."""

import json
import os
import zlib

SILENCE = 0.8        # тиша на шині, після якої вважаємо потік вичерпаним
LIST_TIMEOUT = 3.0
BATCH = 4            # не більше чотирьох дозапитів за пачку
MAX_ROUNDS = 20


class ParamSync:
    def __init__(self, link):
        self.link = link
        self.state = "idle"
        self.values: dict[str, float] = {}
        self.count = 0
        self.got: list[bool] = []
        self.received = 0
        self.cursor = 0
        self.rounds = 0
        self.list_attempts = 0
        self.pacing = 0.1
        self.last_rx = 0.0
        self.last_tx = 0.0

    @property
    def done(self) -> bool:
        return self.state == "done"

    @property
    def failed(self) -> bool:
        return self.state == "failed"

    def start(self, tsys: int, tcomp: int, now: float) -> None:
        self.tsys, self.tcomp = tsys, tcomp
        self.values.clear()
        self.count = 0
        self.got = []
        self.received = 0
        self.cursor = 0
        self.rounds = 0
        self.list_attempts = 0
        self.state = "wait_list"
        self._send_request_list(now)

    def _send_request_list(self, now: float) -> None:
        self.link.mav.param_request_list_send(self.tsys, self.tcomp)
        self.list_attempts += 1
        self.last_tx = self.last_rx = now
        print("[2/5] PARAM_REQUEST_LIST → чекаємо потік PARAM_VALUE")

    def on_message(self, msg, now: float) -> None:
        if self.state not in ("wait_list", "recovering"):
            return
        if msg.get_type() != "PARAM_VALUE":
            return
        if (msg.get_srcSystem(), msg.get_srcComponent()) != (self.tsys, self.tcomp):
            return

        self.last_rx = now
        if not self.got:
            if msg.param_count == 0:
                self.state = "done"
                print("[2/5] автопілот повідомив param_count = 0")
                return
            self.count = msg.param_count
            self.got = [False] * self.count
            self.state = "recovering"
            print(f"[2/5] param_count = {self.count}, виділено бітову маску індексів")

        index = msg.param_index
        # 0xFFFF — відповідь на запит за іменем: місця в масці для неї немає.
        if index == 0xFFFF or index >= self.count:
            return

        name = msg.param_id
        if isinstance(name, bytes):
            name = name.decode("ascii", "replace")
        self.values[name.rstrip("\x00")] = float(msg.param_value)

        if not self.got[index]:
            self.got[index] = True
            self.received += 1
            if self.received % 200 == 0:
                print(f"      прийнято {self.received} / {self.count}")
        if self.received == self.count:
            self._finish()

    def tick(self, now: float) -> None:
        if self.state == "wait_list":
            if now - self.last_tx < LIST_TIMEOUT:
                return
            if self.list_attempts >= 3:
                print("[!] автопілот не відповів на PARAM_REQUEST_LIST")
                self.state = "failed"
            else:
                self._send_request_list(now)
            return
        if self.state != "recovering":
            return
        # Дозапити починаємо лише коли потік стих: інакше самі створимо
        # колізію в напівдуплексному ефірі.
        if now - self.last_rx < SILENCE or now - self.last_tx < self.pacing:
            return
        self._request_missing(now)

    def _request_missing(self, now: float) -> None:
        sent = 0
        for offset in range(self.count):
            index = (self.cursor + offset) % self.count
            if self.got[index]:
                continue
            # Порожнє ім'я плюс індекс — адресний дозапит саме цього номера.
            self.link.mav.param_request_read_send(self.tsys, self.tcomp, b"", index)
            self.cursor = index + 1
            sent += 1
            if sent == BATCH:
                break

        if sent == 0:
            self._finish()
            return
        self.last_tx = now
        self.rounds += 1
        if self.rounds == 1 or self.rounds % 5 == 0:
            print(f"      дірки в списку: {self.count - self.received}, "
                  f"дозапит пачкою по {sent} (раунд {self.rounds})")
        if self.rounds > MAX_ROUNDS:
            print(f"[!] {self.count - self.received} параметрів не вичитано за {MAX_ROUNDS} "
                  f"раундів — лінк надто поганий")
            self.state = "failed"

    def _finish(self) -> None:
        self.state = "done"
        print(f"[2/5] вичитано {len(self.values)} параметрів")
        self._check_cache()

    def _check_cache(self) -> None:
        # Стандартного повідомлення «дай хеш параметрів» у MAVLink немає, тож хеш
        # рахує сама станція: збіг із кешем означає, що збережені налаштування чинні.
        blob = json.dumps(self.values, sort_keys=True).encode()
        crc = zlib.crc32(blob)
        path = f"params-{self.tsys}.cache.json"

        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    cached = json.load(fh)
                if cached.get("crc32") == crc:
                    print(f"[2/5] кеш параметрів чинний (CRC32 0x{crc:08x})")
                    return
            except (OSError, ValueError):
                pass  # побитий кеш просто перезапишемо

        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"crc32": crc, "params": self.values}, fh, sort_keys=True)
            print(f"[2/5] кеш параметрів оновлено (CRC32 0x{crc:08x})")
        except OSError as exc:
            print(f"[!] кеш параметрів не записався: {exc}")
