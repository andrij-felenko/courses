"""Фасад над згенерованим парсером: конверт наш, поля — машинні.

Тут перевіряється саме поділ праці. Kaitai знає зсуви й масштаби, але не
знає ні про CRC, ні про версію, ні про те, що telemetry — рівно 8 байтів;
фасад додає це й називає помилки так само, як прошивка.
"""

from __future__ import annotations

import pytest

import golden_vectors as gv
from telemetry import MsgType, ParseError, ProtocolError, StatusCode, crc_matches_schema, decode

pytest.importorskip("kaitaistruct", reason="pip install kaitaistruct")
pytest.importorskip(
    "telemetry_protocol",
    reason="спершу ksc -t python ksy/telemetry_protocol.ksy --outdir generated/python",
)

pytestmark = pytest.mark.kaitai


def test_decode_telemetry():
    decoded = decode(gv.GOLDEN_TELEMETRY)

    assert decoded.msg_type is MsgType.TELEMETRY_REPORT
    assert decoded.seq_id == 0x4A
    assert decoded.envelope.payload_len == 8
    assert decoded.payload.temperature_c == pytest.approx(24.50)
    assert decoded.payload.pressure_hpa == pytest.approx(1013.2)
    assert decoded.payload.alert_active is True
    assert crc_matches_schema(decoded.packet)


def test_decode_negative_temperature():
    decoded = decode(gv.NEGATIVE_TEMPERATURE)

    assert decoded.payload.temp_raw == -312
    assert decoded.payload.temperature_c == pytest.approx(-3.12)
    assert decoded.payload.sensor_fault is True


def test_decode_set_config_and_ack():
    cfg = decode(gv.GOLDEN_SET_CONFIG)
    assert cfg.msg_type is MsgType.CMD_SET_CONFIG
    assert cfg.payload.alert_threshold_c == pytest.approx(85.0)

    ack = decode(gv.GOLDEN_ACK)
    assert ack.msg_type is MsgType.CMD_RESPONSE
    assert ack.payload.target_seq_id == 0x10
    # Kaitai віддає власний enum; звіряємо за числом, а не за іменем класу.
    assert ack.payload.status.value == StatusCode.OK


def test_decode_ping():
    decoded = decode(gv.GOLDEN_PING)

    assert decoded.msg_type is MsgType.CMD_PING
    assert bytes(decoded.payload) == b""


@pytest.mark.parametrize(
    ("frame", "code"),
    [
        (gv.flip_bit(gv.GOLDEN_TELEMETRY, 6), ParseError.INVALID_CRC),
        (gv.build_frame(0x7F, b"\x01\x02"), ParseError.UNKNOWN_MSG),
        (
            gv.build_frame(gv.MSG_TELEMETRY, gv.telemetry_payload(0, 0, 0), version=0x02),
            ParseError.UNSUPPORTED_VERSION,
        ),
    ],
)
def test_facade_refuses_what_schema_lets_through(frame, code):
    # Сирий Kaitai усі три кадри розбирає без нарікань — і саме тому
    # прикладний рівень не можна лишати на самій схемі.
    with pytest.raises(ProtocolError) as err:
        decode(frame)
    assert err.value.code is code
