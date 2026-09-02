"""Прикладний бік розбору: конверт своїми руками, поля — згенерованим кодом.

Розподіл праці такий:

* ``check_envelope`` перевіряє все, що схема не перевіряє або перевіряє
  надто пізно (маркери, межі, сума, версія, відповідність довжини типові)
  і робить це В ТОМУ САМОМУ ПОРЯДКУ, що прошивка на C. Чистий Python —
  працює і без ksc;
* ``decode`` після цього віддає кадр згенерованому парсерові, тож зсуви
  полів у Python не переписуються взагалі.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

from .crc import crc16_ccitt, verify
from .errors import ParseError, ProtocolError
from .wire import EOF, FOOTER_LEN, HEADER_LEN, MAX_PAYLOAD, MIN_FRAME, SOF, VERSION, MsgType

_parser_class: Any | None = None


def generated_parser() -> Any:
    """Клас TelemetryProtocol із машинного виходу ksc.

    Імпорт лінивий: рамкування, CRC й серіалізація мусять працювати на
    голому Python, без рантайму kaitaistruct і без згенерованого модуля.
    """
    global _parser_class
    if _parser_class is None:
        try:
            module = importlib.import_module("telemetry_protocol")
        except ModuleNotFoundError as exc:  # pragma: no cover — залежить від оточення
            raise RuntimeError(
                "модуль telemetry_protocol не згенеровано; виконай "
                "ksc -t python ksy/telemetry_protocol.ksy --outdir generated/python"
            ) from exc
        _parser_class = module.TelemetryProtocol
    return _parser_class


@dataclass(frozen=True, slots=True)
class Envelope:
    """Заголовок і хвіст кадру, перевірені до звернення до навантаження."""

    version: int
    msg_type: MsgType
    seq_id: int
    payload_len: int
    crc16: int
    payload: bytes


@dataclass(frozen=True, slots=True)
class DecodedFrame:
    """Перевірений конверт плюс розібраний згенерованим кодом об'єкт."""

    envelope: Envelope
    packet: Any

    @property
    def msg_type(self) -> MsgType:
        return self.envelope.msg_type

    @property
    def seq_id(self) -> int:
        return self.envelope.seq_id

    @property
    def payload(self) -> Any:
        return self.packet.payload


def check_envelope(frame: bytes | bytearray | memoryview) -> Envelope:
    """Ті самі сім перевірок, що й у proto_parse_frame, у тому самому порядку."""
    if not isinstance(frame, (bytes, bytearray, memoryview)):
        raise TypeError(f"очікували байти, дістали {type(frame).__name__}")
    view = memoryview(frame)

    if len(view) < MIN_FRAME:
        raise ProtocolError(
            ParseError.INVALID_LEN, f"кадр {len(view)} байт, мінімум {MIN_FRAME}"
        )
    if view[0] != SOF:
        raise ProtocolError(ParseError.INVALID_SOF, f"перший байт 0x{view[0]:02X}")
    if view[-1] != EOF:
        raise ProtocolError(ParseError.INVALID_EOF, f"останній байт 0x{view[-1]:02X}")

    # Довжину звіряємо з фактичним розміром буфера ДО того, як торкнутися
    # навантаження: заявлені 8 байтів у чотирибайтовому кадрі — це не
    # «дочитаємо», а вихід за межі.
    declared = int.from_bytes(view[4:6], "little")
    if declared > MAX_PAYLOAD:
        raise ProtocolError(
            ParseError.INVALID_LEN, f"заявлено {declared} байт понад стелю {MAX_PAYLOAD}"
        )
    if len(view) != HEADER_LEN + declared + FOOTER_LEN:
        raise ProtocolError(
            ParseError.INVALID_LEN,
            f"заявлено {declared} байт, у буфері {len(view) - HEADER_LEN - FOOTER_LEN}",
        )

    # Суму перевіряємо раніше за версію й тип: до неї жодному полю кадру
    # вірити не можна, а межі вже перевірено вище.
    written, calculated = verify(view, declared)
    if written != calculated:
        raise ProtocolError(
            ParseError.INVALID_CRC, f"у кадрі 0x{written:04X}, порахували 0x{calculated:04X}"
        )

    if view[1] != VERSION:
        raise ProtocolError(ParseError.UNSUPPORTED_VERSION, f"версія {view[1]}, чинна {VERSION}")

    try:
        msg_type = MsgType(view[2])
    except ValueError as exc:
        # Кадр майбутньої версії протоколу: штатна відмова, не падіння.
        raise ProtocolError(ParseError.UNKNOWN_MSG, f"msg_id 0x{view[2]:02X}") from exc

    from .wire import PAYLOAD_SIZE

    expected = PAYLOAD_SIZE[msg_type]
    if expected != declared:
        raise ProtocolError(
            ParseError.INVALID_LEN,
            f"{msg_type.name} — це {expected} байт, заявлено {declared}",
        )

    return Envelope(
        version=view[1],
        msg_type=msg_type,
        seq_id=view[3],
        payload_len=declared,
        crc16=written,
        payload=bytes(view[HEADER_LEN : HEADER_LEN + declared]),
    )


def decode(frame: bytes | bytearray | memoryview) -> DecodedFrame:
    """Повний розбір: конверт руками, поля — згенерованим парсером."""
    envelope = check_envelope(frame)
    parser = generated_parser()

    import kaitaistruct

    try:
        packet = parser.from_bytes(bytes(frame))
    except EOFError as exc:  # pragma: no cover — конверт ловить це раніше
        raise ProtocolError(ParseError.INVALID_LEN, "потік урвався всередині кадру") from exc
    except kaitaistruct.ValidationNotEqualError as exc:  # pragma: no cover — те саме
        raise ProtocolError(ParseError.INVALID_SOF, f"маркер не збігся: {exc}") from exc

    return DecodedFrame(envelope=envelope, packet=packet)


def crc_matches_schema(packet: Any) -> bool:
    """Звіряє суму, беручи проміжок байтів з інстансу crc_input самої схеми.

    Сенс у тому, що жодного зсуву тут не написано: змінився формат
    заголовка — змінився й crc_input, а цей код лишився чинним.
    """
    return crc16_ccitt(packet.crc_input) == packet.crc16
