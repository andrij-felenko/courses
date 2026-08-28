import time
from collections import defaultdict
from pymavlink import mavutil

LIST_SILENCE, STREAM_SILENCE, READ_ACK = 5.0, 3.0, 1.0   # секунди
LIST_RETRIES, TRIES_PER_INDEX, BATCH   = 4, 5, 10


class ParamFetcher:
    """Добірник параметрів: чеклист номерів, таймер тиші, пачка точкових запитів."""

    def __init__(self, conn, target_sys, default_comp):
        self.conn, self.sys, self.default_comp = conn, target_sys, default_comp

        # Під одним апаратом кілька компонентів (автопілот, підвіс, камера),
        # і в кожного свій param_count та своя незалежна нумерація.
        self.total     = {}                 # компонент → param_count
        self.waiting   = {}                 # компонент → {номер: скільки разів просили}
        self.failed    = defaultdict(set)   # компонент → номери, на яких здалися
        self.got       = defaultdict(dict)  # компонент → {ім'я: (значення, тип)}
        self.in_flight = {}                 # (компонент, номер) → дедлайн

        self.awaiting_list = False          # чекаємо першої відповіді на запит списку
        self.batch_on      = False          # потік вичерпався, працює добір
        self.give_up       = False          # борт не озвався зовсім
        self.silence_deadline = 0.0

    def start(self):
        self._send_request_list()
        self.list_attempts = 1
        self.awaiting_list = True
        self.list_deadline = time.monotonic() + LIST_SILENCE
