"""Звірка згенерованого Kaitai-парсера з еталонними векторами.

Модуль telemetry_protocol у sys.path кладе кодогенератор:

    ksc -t python ksy/telemetry_protocol.ksy --outdir generated/python

Тому тест не знає нічого про зсуви полів — він знає лише числа, які
мусили доїхати. Розійдеться схема з прошивкою — розсиплеться саме тут.

Без згенерованого модуля весь файл пропускається; конверт, суму й
рамкування перевіряють сусідні тести, яким ksc не потрібен.
"""

import pytest

import golden_vectors as gv
from telemetry import ParseError, ProtocolError, check_envelope, crc_matches_schema

kaitaistruct = pytest.importorskip("kaitaistruct", reason="pip install kaitaistruct")
_generated = pytest.importorskip(
    "telemetry_protocol",
    reason="спершу ksc -t python ksy/telemetry_protocol.ksy --outdir generated/python",
)

TelemetryProtocol = _generated.TelemetryProtocol
ValidationNotEqualError = kaitaistruct.ValidationNotEqualError

pytestmark = pytest.mark.kaitai


def test_golden_telemetry_packet():
    pkt = TelemetryProtocol.from_bytes(gv.GOLDEN_TELEMETRY)

    assert pkt.sof == b"\xaa"
    assert pkt.version == 1
    assert pkt.msg_id == TelemetryProtocol.MsgType.telemetry_report
    assert pkt.seq_id == 0x4A
    assert pkt.payload_len == 8
    assert isinstance(pkt.payload, TelemetryProtocol.MsgTelemetry)

    assert pkt.payload.temp_raw == 2450
    assert pkt.payload.pressure_raw == 10132
    assert pkt.payload.voltage_mv == 3300
    assert pkt.payload.flags == gv.FLAG_ALERT
    assert pkt.payload.reserved == 0x00

    # instances зі схеми: масштабування живе в згенерованому коді
    assert pkt.payload.temperature_c == pytest.approx(24.50)
    assert pkt.payload.pressure_hpa == pytest.approx(1013.2)
    assert pkt.payload.alert_active is True
    assert pkt.payload.sensor_fault is False

    written, calculated = gv.frame_crc(gv.GOLDEN_TELEMETRY)
    assert pkt.crc16 == written == calculated
    assert pkt.eof == b"\x55"


def test_crc_input_instance_marks_the_right_span():
    # Проміжок для суми віддає САМА схема — зсуви не переписуються в жодній
    # цільовій мові, а сума лишається справою застосунку.
    pkt = TelemetryProtocol.from_bytes(gv.GOLDEN_TELEMETRY)

    assert bytes(pkt.crc_input) == gv.GOLDEN_TELEMETRY[1 : -gv.FOOTER_LEN]
    assert crc_matches_schema(pkt)


def test_negative_temperature_sign():
    # На дроті — 0xC8 0xFE (little-endian), у полі — -312.
    assert gv.NEGATIVE_TEMPERATURE[6:8] == b"\xc8\xfe"

    pkt = TelemetryProtocol.from_bytes(gv.NEGATIVE_TEMPERATURE)
    assert pkt.payload.temp_raw == -312
    assert pkt.payload.temperature_c == pytest.approx(-3.12)
    assert pkt.payload.sensor_fault is True


def test_set_config_packet():
    pkt = TelemetryProtocol.from_bytes(gv.GOLDEN_SET_CONFIG)

    assert pkt.msg_id == TelemetryProtocol.MsgType.cmd_set_config
    assert pkt.payload_len == 5
    assert pkt.payload.sample_rate_hz == 100
    # На дроті — сирі соті градуса, фізичну величину віддає instance.
    assert pkt.payload.alert_threshold_raw == 8500
    assert pkt.payload.alert_threshold_c == pytest.approx(85.0)
    assert pkt.payload.flags_enable == 0x03


def test_ack_status_enum():
    pkt = TelemetryProtocol.from_bytes(gv.GOLDEN_ACK)

    assert pkt.msg_id == TelemetryProtocol.MsgType.cmd_response
    assert pkt.payload.target_seq_id == 0x10
    assert pkt.payload.status == TelemetryProtocol.StatusCode.ok


def test_ping_has_empty_payload():
    pkt = TelemetryProtocol.from_bytes(gv.GOLDEN_PING)

    assert pkt.msg_id == TelemetryProtocol.MsgType.cmd_ping
    assert pkt.payload_len == 0
    # Для ping у схемі немає окремого типу — Kaitai віддає сирі байти.
    assert bytes(pkt.payload) == b""


@pytest.mark.parametrize("sof", [0x00, 0xAB])
def test_invalid_sof_rejected(sof):
    frame = gv.build_frame(gv.MSG_TELEMETRY, gv.telemetry_payload(0, 1000, 3300), sof=sof)
    # contents: [0xaa] у схемі — це перевірка, а не документація.
    with pytest.raises(ValidationNotEqualError):
        TelemetryProtocol.from_bytes(frame)


def test_invalid_eof_rejected():
    frame = gv.build_frame(gv.MSG_TELEMETRY, gv.telemetry_payload(0, 1000, 3300), eof=0x00)
    with pytest.raises(ValidationNotEqualError):
        TelemetryProtocol.from_bytes(frame)


def test_crc_mismatch_is_caught_outside_schema():
    # Псуємо байт навантаження, суму лишаємо стару.
    frame = gv.flip_bit(gv.GOLDEN_TELEMETRY, 6)

    pkt = TelemetryProtocol.from_bytes(frame)  # структурно кадр цілий
    written, calculated = gv.frame_crc(frame)

    assert pkt.crc16 == written
    assert calculated != written  # а от відкидає такий кадр уже наш код
    with pytest.raises(ProtocolError) as err:
        check_envelope(frame)
    assert err.value.code is ParseError.INVALID_CRC


def test_declared_length_beyond_buffer():
    # Заголовок обіцяє 8 байтів, фізично їх 4.
    frame = gv.build_frame(
        gv.MSG_TELEMETRY,
        gv.telemetry_payload(2450, 10132, 3300)[:4],
        declared_len=8,
        seq_id=0x01,
    )
    with pytest.raises(EOFError):
        TelemetryProtocol.from_bytes(frame)


def test_length_mismatch_for_type_underflows_substream():
    # Довжина сходиться з буфером, але не з типом: telemetry — це 8 байтів.
    frame = gv.build_frame(
        gv.MSG_TELEMETRY, gv.telemetry_payload(2450, 10132, 3300)[:5], seq_id=0x02
    )
    # size: payload_len дає підпотік на 5 байтів, а msg_telemetry читає з
    # нього 8 — розбір гине зсередини, без внятного коду помилки.
    with pytest.raises(EOFError):
        TelemetryProtocol.from_bytes(frame)

    # Саме тому перевірку довжини дублюють ручні парсери
    # (ERR_INVALID_LEN / ParseError::InvalidLen / check_envelope).
    with pytest.raises(ProtocolError) as err:
        check_envelope(frame)
    assert err.value.code is ParseError.INVALID_LEN


def test_unsupported_version_is_not_schema_business():
    frame = gv.build_frame(gv.MSG_TELEMETRY, gv.telemetry_payload(0, 1000, 3300), version=0x02)

    pkt = TelemetryProtocol.from_bytes(frame)
    # Схема свідомо не валідує version: кадр наступної мажорної версії
    # мусить розібратися структурно, а відкинути його — рішення застосунку.
    assert pkt.version == 2
    with pytest.raises(ProtocolError) as err:
        check_envelope(frame)
    assert err.value.code is ParseError.UNSUPPORTED_VERSION


def test_unknown_msg_id_survives():
    frame = gv.build_frame(0x7F, b"\x01\x02", seq_id=0x03)

    pkt = TelemetryProtocol.from_bytes(frame)
    # resolve_enum віддає сире число, коли значення немає в enums::msg_type,
    # а payload без відповідної гілки switch-on лишається байтами.
    assert pkt.msg_id == 0x7F
    assert bytes(pkt.payload) == b"\x01\x02"

    # Застосунок такий кадр не виконує, але й не падає на ньому.
    with pytest.raises(ProtocolError) as err:
        check_envelope(frame)
    assert err.value.code is ParseError.UNKNOWN_MSG


def test_all_vectors_have_consistent_crc():
    for name, frame in gv.ALL_GOLDEN.items():
        written, calculated = gv.frame_crc(frame)
        assert written == calculated, f"вектор {name} зібрано з битою сумою"
