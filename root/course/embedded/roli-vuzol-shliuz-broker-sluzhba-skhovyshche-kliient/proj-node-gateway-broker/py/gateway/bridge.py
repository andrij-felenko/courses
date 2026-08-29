"""Демон шлюзу: міст між бінарним польовим каналом і MQTT-брокером.

Три обов'язки, і всі три видно в коді нижче:
  * угору — розібрати кадр, відсіяти надлишковий за deadband, збагатити
    метаданими й опублікувати JSON;
  * униз — прийняти команду з брокера, скласти бінарний кадр і надіслати
    її саме тому вузлові, чиє з'єднання зараз живе;
  * замкнути контур — дочекатися квитанції, оновити цифрового двійника,
    а якщо квитанції немає — повторити й зрештою зізнатися в невдачі.
"""

from __future__ import annotations

import json
import socket
import threading
import time
from collections import deque
from dataclasses import dataclass, field

import paho.mqtt.client as mqtt

from . import protocol as proto
from .framer import StreamFramer

MQTT_HOST = "localhost"
MQTT_PORT = 1883
FIELD_HOST = "0.0.0.0"
FIELD_PORT = 9000

GATEWAY_ID = "gw_edge_01"
TENANT_ID = "org_alpha"

DEADBAND_C = 0.2        # менша зміна температури в хмару не їде
HEARTBEAT_S = 60.0      # але раз на хвилину вузол мусить озватися
ACK_TIMEOUT_S = 2.0     # скільки чекати на квитанцію
ACK_RETRIES = 3         # і скільки разів повторити команду
BACKLOG_LIMIT = 500     # скільки повідомлень тримати, поки брокер недосяжний


@dataclass
class PendingCommand:
    seq: int
    cmd_id: int
    value: int
    attempts: int = 1
    deadline: float = 0.0


@dataclass
class Twin:
    """Цифровий двійник вузла: чого хочемо і що вузол підтвердив."""

    node_id: int
    desired_relay: bool | None = None
    reported_relay: bool | None = None
    last_seen: float = 0.0
    pending: PendingCommand | None = None


@dataclass
class NodeSession:
    """Живе з'єднання одного вузла плюс стан його приймача."""

    node_id: int
    sock: socket.socket
    peer: str
    framer: StreamFramer
    lock: threading.Lock = field(default_factory=threading.Lock)

    def send(self, frame: bytes) -> bool:
        with self.lock:
            try:
                self.sock.sendall(frame)
                return True
            except OSError as exc:
                print(f"[GW] вузол {self.node_id}: запис у канал впав — {exc}")
                return False


class GatewayBridge:
    def __init__(self) -> None:
        self._sessions: dict[int, NodeSession] = {}
        self._twins: dict[int, Twin] = {}
        self._deadband: dict[int, tuple[float, float]] = {}   # node_id -> (temp, ts)
        self._state_lock = threading.Lock()
        self._cmd_seq = 0

        self._backlog: deque[tuple[str, str]] = deque(maxlen=BACKLOG_LIMIT)
        self._online = False
        self._stop = threading.Event()

        self._mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                 client_id=f"gateway_{GATEWAY_ID}")
        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_disconnect = self._on_disconnect
        self._mqtt.on_message = self._on_command

    # ---------------------------------------------------------------- MQTT

    def _on_connect(self, client, _userdata, _flags, reason_code, _props=None) -> None:
        if reason_code != 0:
            print(f"[GW] брокер відмовив: {reason_code}")
            return
        topic = f"command/{TENANT_ID}/{GATEWAY_ID}/+"
        client.subscribe(topic, qos=1)
        self._online = True
        print(f"[GW] брокер підключено, підписка на {topic}")
        self._flush_backlog()

    def _on_disconnect(self, _client, _userdata, _flags, reason_code, _props=None) -> None:
        self._online = False
        print(f"[GW] зв'язок із брокером утрачено ({reason_code}), publish іде в накопичувач")

    def _publish(self, topic: str, doc: dict) -> None:
        """Публікація, що не падає разом із мережею.

        Коли брокер недосяжний, paho складає повідомлення у власну чергу й
        зрештою переповнює її. Тому невдалі публікації тримаємо самі — в
        обмеженому накопичувачі, де найстаріше витісняється найновішим.
        """
        payload = json.dumps(doc, ensure_ascii=False)
        if not self._online:
            self._backlog.append((topic, payload))
            return
        info = self._mqtt.publish(topic, payload, qos=1)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"[GW] publish у {topic} відхилено (rc={info.rc}) — у накопичувач")
            self._backlog.append((topic, payload))

    def _flush_backlog(self) -> None:
        sent = 0
        while self._backlog and self._online:
            topic, payload = self._backlog[0]
            info = self._mqtt.publish(topic, payload, qos=1)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                break
            self._backlog.popleft()
            sent += 1
        if sent:
            print(f"[GW] з накопичувача віддано {sent} повідомлень")

    # ------------------------------------------------------- команди вниз

    def _on_command(self, _client, _userdata, msg) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            node_id = int(msg.topic.rsplit("/", 1)[-1].removeprefix("node_"))
            cmd_id = int(payload.get("cmd_id", proto.CMD_SET_RELAY))
            value = int(payload.get("val", 0))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"[GW] команду з {msg.topic} відкинуто — {exc}")
            return

        with self._state_lock:
            self._cmd_seq += 1
            seq = self._cmd_seq
            twin = self._twins.setdefault(node_id, Twin(node_id=node_id))
            if cmd_id == proto.CMD_SET_RELAY:
                twin.desired_relay = bool(value)
            twin.pending = PendingCommand(seq=seq, cmd_id=cmd_id, value=value,
                                          deadline=time.monotonic() + ACK_TIMEOUT_S)

        print(f"[GW ← MQTT] вузол {node_id}: cmd=0x{cmd_id:02X} val={value} (seq={seq})")
        self._send_command(node_id, seq, cmd_id, value)

    def _send_command(self, node_id: int, seq: int, cmd_id: int, value: int) -> None:
        session = self._sessions.get(node_id)
        if session is None:
            print(f"[GW] вузол {node_id} зараз не на зв'язку — команду не віддано")
            return
        if not session.send(proto.encode_command(node_id, seq, cmd_id, value)):
            return
        print(f"[GW → вузол {node_id}] кадр команди {proto.FRAME_SIZE} Б у польовий канал")

    def _watch_pending(self) -> None:
        """Замикання контуру: без квитанції команду повторюємо, потім здаємося."""
        while not self._stop.wait(0.5):
            now = time.monotonic()
            retries: list[tuple[int, PendingCommand]] = []
            failures: list[tuple[int, PendingCommand]] = []

            with self._state_lock:
                for twin in self._twins.values():
                    cmd = twin.pending
                    if cmd is None or now < cmd.deadline:
                        continue
                    if cmd.attempts >= ACK_RETRIES:
                        twin.pending = None
                        failures.append((twin.node_id, cmd))
                    else:
                        cmd.attempts += 1
                        cmd.deadline = now + ACK_TIMEOUT_S
                        retries.append((twin.node_id, cmd))

            for node_id, cmd in retries:
                print(f"[GW] вузол {node_id}: квитанції немає, спроба {cmd.attempts}")
                self._send_command(node_id, cmd.seq, cmd.cmd_id, cmd.value)

            for node_id, cmd in failures:
                print(f"[GW] вузол {node_id}: команда seq={cmd.seq} не підтверджена")
                self._publish(self._state_topic(node_id), {
                    "timestamp": _utc_now(),
                    "gateway_id": GATEWAY_ID,
                    "node_id": node_id,
                    "command_seq": cmd.seq,
                    "result": "no_ack",
                })

    # -------------------------------------------------------- кадри вгору

    def _should_forward(self, node_id: int, temp_c: float) -> bool:
        now = time.monotonic()
        last = self._deadband.get(node_id)
        if last is None or abs(temp_c - last[0]) >= DEADBAND_C or now - last[1] >= HEARTBEAT_S:
            self._deadband[node_id] = (temp_c, now)
            return True
        return False

    def _handle_telemetry(self, t: proto.Telemetry, rssi_dbm: int) -> None:
        with self._state_lock:
            twin = self._twins.setdefault(t.node_id, Twin(node_id=t.node_id))
            twin.reported_relay = t.relay_on
            twin.last_seen = time.time()

        if not self._should_forward(t.node_id, t.temp_c):
            print(f"[GW] deadband: вузол {t.node_id} ({t.temp_c:.2f} °C) відсіяно локально")
            return

        self._publish(f"telemetry/{TENANT_ID}/{GATEWAY_ID}/node_{t.node_id}", {
            "timestamp": _utc_now(),
            "gateway_id": GATEWAY_ID,
            "node_id": t.node_id,
            "seq": t.seq,
            "metrics": {
                "temperature": round(t.temp_c, 2),
                "battery_mv": t.battery_mv,
                "relay_status": t.relay_on,
            },
            "sensor_fault": t.sensor_fault,
            "rssi_dbm": rssi_dbm,
        })
        print(f"[GW → MQTT] вузол {t.node_id}: {t.temp_c:.2f} °C, {t.battery_mv} мВ")

    def _handle_ack(self, a: proto.Ack) -> None:
        with self._state_lock:
            twin = self._twins.setdefault(a.node_id, Twin(node_id=a.node_id))
            cmd = twin.pending
            if cmd is None or cmd.seq != a.seq:
                print(f"[GW] вузол {a.node_id}: квитанція seq={a.seq} нікого не чекала")
                return
            twin.pending = None
            twin.reported_relay = a.relay_on

        status = {proto.ACK_OK: "ok",
                  proto.ACK_UNKNOWN_CMD: "unknown_command",
                  proto.ACK_BAD_VALUE: "bad_value"}.get(a.status, "unknown")
        print(f"[GW] вузол {a.node_id}: команду seq={a.seq} підтверджено ({status}), "
              f"реле={'увімкнено' if a.relay_on else 'вимкнено'}")

        self._publish(self._state_topic(a.node_id), {
            "timestamp": _utc_now(),
            "gateway_id": GATEWAY_ID,
            "node_id": a.node_id,
            "command_seq": a.seq,
            "result": status,
            "reported": {"relay_status": a.relay_on, "sensor_fault": a.sensor_fault},
        })

    @staticmethod
    def _state_topic(node_id: int) -> str:
        return f"state/{TENANT_ID}/{GATEWAY_ID}/node_{node_id}"

    # ------------------------------------------------------- польовий бік

    def _serve_node(self, sock: socket.socket, addr: tuple[str, int]) -> None:
        peer = f"{addr[0]}:{addr[1]}"
        framer = StreamFramer()
        session: NodeSession | None = None
        sock.settimeout(HEARTBEAT_S * 2)
        print(f"[GW] польове з'єднання {peer}")

        try:
            while not self._stop.is_set():
                try:
                    chunk = sock.recv(256)
                except socket.timeout:
                    print(f"[GW] {peer} мовчить довше за два heartbeat — рвемо з'єднання")
                    break
                except OSError as exc:
                    print(f"[GW] {peer}: читання впало — {exc}")
                    break
                if not chunk:
                    break

                for raw in framer.feed(chunk):
                    try:
                        frame = proto.decode(raw)
                    except proto.FrameError as exc:
                        print(f"[GW] {peer}: кадр відкинуто — {exc}")
                        continue

                    if session is None:
                        # Хто саме на тому кінці, ми дізнаємося з першого ж
                        # валідного кадру: адреса вузла живе в кадрі, не в сокеті.
                        session = NodeSession(node_id=frame.node_id, sock=sock,
                                              peer=peer, framer=framer)
                        self._sessions[frame.node_id] = session
                        print(f"[GW] {peer} — це вузол {frame.node_id}")

                    if isinstance(frame, proto.Telemetry):
                        self._handle_telemetry(frame, rssi_dbm=-68)
                    elif isinstance(frame, proto.Ack):
                        self._handle_ack(frame)
                    else:
                        print(f"[GW] {peer}: команда з польового боку — ігноруємо")
        finally:
            if session is not None and self._sessions.get(session.node_id) is session:
                del self._sessions[session.node_id]
            sock.close()
            print(f"[GW] {peer} від'єднано, викинуто на ресинхронізації "
                  f"{framer.resync_drops} Б на {framer.frames_accepted} кадрів")

    def run(self) -> None:
        self._mqtt.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        self._mqtt.loop_start()

        threading.Thread(target=self._watch_pending, daemon=True).start()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((FIELD_HOST, FIELD_PORT))
        server.listen(8)
        server.settimeout(1.0)
        print(f"[GW] польовий канал слухає {FIELD_HOST}:{FIELD_PORT}")

        try:
            while True:
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue   # даємо циклу шанс помітити Ctrl+C
                threading.Thread(target=self._serve_node, args=(conn, addr),
                                 daemon=True).start()
        except KeyboardInterrupt:
            print("\n[GW] зупинка")
        finally:
            self._stop.set()
            server.close()
            self._mqtt.loop_stop()
            self._mqtt.disconnect()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
