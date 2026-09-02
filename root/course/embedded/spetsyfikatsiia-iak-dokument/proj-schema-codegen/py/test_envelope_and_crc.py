"""Сума, серіалізатор і конверт — та частина, що працює без ksc.

Головний тут не окремий негативний випадок, а перший тест: байти, які
складає telemetry.encoder, мусять збігтися з еталонними векторами, які
golden_vectors склали незалежно від нього. Розійдуться — значить хтось
із двох перестав відповідати схемі.
"""

from __future__ import annotations

import pytest

import golden_vectors as gv
from telemetry import (
    CRC16_CHECK_VALUE,
    CRC16_CHECK_VECTOR,
    Ack,
    ParseError,
    Ping,
    ProtocolError,
    SetConfig,
    StatusCode,
    Telemetry,
    build_frame,
    check_envelope,
    crc16_ccitt,
    payload_size,
)
from telemetry.wire import MsgType


def test_crc_check_vector():
    # Те саме число стоїть static_assert-ом у C++ і assert-ом у C.
    assert crc16_ccitt(CRC16_CHECK_VECTOR) == CRC16_CHECK_VALUE


def test_crc_matches_reference_implementation():
    for name, frame in gv.ALL_GOLDEN.items():
        written, calculated = gv.frame_crc(frame)
        assert crc16_ccitt(frame[1 : -gv.FOOTER_LEN]) == calculated == written, name


@pytest.mark.parametrize(
    ("payload", "seq_id", "expected"),
    [
        (
            Telemetry(temp_raw=2450, pressure_raw=10132, voltage_mv=3300, flags=gv.FLAG_ALERT),
            0x4A,
            gv.GOLDEN_TELEMETRY,
        ),
        (
            Telemetry(
                temp_raw=-312, pressure_raw=10000, voltage_mv=3290, flags=gv.FLAG_SENSOR_FAULT
            ),
            0x4B,
            gv.NEGATIVE_TEMPERATURE,
        ),
        (
            SetConfig(sample_rate_hz=100, alert_threshold_raw=8500, flags_enable=0x03),
            0x10,
            gv.GOLDEN_SET_CONFIG,
        ),
        (Ack(target_seq_id=0x10, status=StatusCode.OK), 0x11, gv.GOLDEN_ACK),
        (Ping(), 0x12, gv.GOLDEN_PING),
    ],
)
def test_encoder_reproduces_golden_vectors(payload, seq_id, expected):
    assert build_frame(payload, seq_id=seq_id) == expected


def test_negative_temperature_lands_as_twos_complement():
    frame = build_frame(
        Telemetry(temp_raw=-312, pressure_raw=10000, voltage_mv=3290), seq_id=0x4B
    )
    # 0xFEC8 у доповняльному коді, молодший байт перший.
    assert frame[6:8] == b"\xc8\xfe"


def test_from_physical_rounds_to_sensor_codes():
    payload = Telemetry.from_physical(
        temperature_c=24.5, pressure_hpa=1013.2, voltage_mv=3300, alert=True
    )
    assert payload.temp_raw == 2450
    assert payload.pressure_raw == 10132
    assert payload.flags == gv.FLAG_ALERT
    assert payload.temperature_c == pytest.approx(24.5)

    cold = Telemetry.from_physical(temperature_c=-3.12, pressure_hpa=1000.0, voltage_mv=3290)
    assert cold.temp_raw == -312

    cfg = SetConfig.from_physical(sample_rate_hz=100, alert_threshold_c=85.0, flags_enable=0x03)
    assert cfg.alert_threshold_raw == 8500


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("temp_raw", 40000),  # не влізе в s2
        ("temp_raw", -40000),
        ("pressure_raw", -1),  # u2 від'ємних не тримає
        ("voltage_mv", 70000),
        ("flags", 256),
    ],
)
def test_encoder_refuses_out_of_range(field, value):
    kwargs = {"temp_raw": 0, "pressure_raw": 0, "voltage_mv": 0} | {field: value}
    with pytest.raises(ValueError, match=field):
        Telemetry(**kwargs)


def test_encoder_refuses_wrong_type():
    with pytest.raises(TypeError):
        Telemetry(temp_raw=24.5, pressure_raw=0, voltage_mv=0)


def test_payload_size_table_matches_schema():
    assert payload_size(MsgType.CMD_PING) == 0
    assert payload_size(0x02) == 5
    assert payload_size(0x20) == 8
    assert payload_size(0x80) == 2
    assert payload_size(0x7F) is None


def test_envelope_of_golden_frames():
    envelope = check_envelope(gv.GOLDEN_TELEMETRY)
    assert envelope.msg_type is MsgType.TELEMETRY_REPORT
    assert envelope.seq_id == 0x4A
    assert envelope.payload_len == 8
    assert envelope.payload == gv.GOLDEN_TELEMETRY[6:14]
    assert envelope.crc16 == gv.frame_crc(gv.GOLDEN_TELEMETRY)[0]

    assert check_envelope(gv.GOLDEN_PING).payload == b""


def _negative_cases():
    good = gv.telemetry_payload(2450, 10132, 3300)
    return [
        (b"\xaa\x01\x20", ParseError.INVALID_LEN),
        (gv.GOLDEN_TELEMETRY[:8], ParseError.INVALID_LEN),
        (gv.build_frame(gv.MSG_TELEMETRY, good, sof=0x00), ParseError.INVALID_SOF),
        (gv.build_frame(gv.MSG_TELEMETRY, good, eof=0x00), ParseError.INVALID_EOF),
        (gv.flip_bit(gv.GOLDEN_TELEMETRY, 6), ParseError.INVALID_CRC),
        (gv.build_frame(gv.MSG_TELEMETRY, good[:4], declared_len=8), ParseError.INVALID_LEN),
        (gv.build_frame(gv.MSG_TELEMETRY, good[:5]), ParseError.INVALID_LEN),
        (gv.build_frame(gv.MSG_TELEMETRY, good, version=0x02), ParseError.UNSUPPORTED_VERSION),
        (gv.build_frame(0x7F, b"\x01\x02"), ParseError.UNKNOWN_MSG),
        (gv.build_frame(gv.MSG_TELEMETRY, b"\x00" * 65), ParseError.INVALID_LEN),
    ]


@pytest.mark.parametrize(("frame", "code"), _negative_cases())
def test_envelope_rejects_broken_frames(frame, code):
    # Той самий перелік, що ганяють C і C++ у своїх самотестах.
    with pytest.raises(ProtocolError) as err:
        check_envelope(frame)
    assert err.value.code is code
    assert str(err.value).startswith(code.value)


def test_envelope_refuses_non_bytes():
    with pytest.raises(TypeError):
        check_envelope("AA0120")


def test_crc_checked_before_version_and_type():
    # Кадр із чужою версією І битою сумою мусить дати саме CRC: до суми
    # жодному полю заголовка вірити не можна.
    frame = bytearray(gv.build_frame(gv.MSG_TELEMETRY, gv.telemetry_payload(0, 0, 0), version=0x02))
    frame[6] ^= 0x01
    with pytest.raises(ProtocolError) as err:
        check_envelope(bytes(frame))
    assert err.value.code is ParseError.INVALID_CRC
