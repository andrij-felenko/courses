"""
Низькорівневий модуль кадрування промислового протоколу Modbus RTU.

Реалізує табличний розрахунок контрольної суми CRC-16 (поліном 0xA001),
пакування команд запису 16-бітних регістрів утримання (функція 0x06)
та валідацію двійкових кадрів відповідей і протокольних кодів винятків.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Optional


# ============================================================================
# ВИНЯТКИ ДВІЙКОВОГО КАДРУВАННЯ MODBUS
# ============================================================================

class ModbusFrameError(Exception):
    """Базовий виняток низькорівневого розбору кадру Modbus RTU."""
    pass


class ModbusCrcError(ModbusFrameError):
    """Помилка невідповідності контрольної суми CRC-16 (пошкоджені байти в лінії)."""
    pass


class ModbusProtocolViolation(ModbusFrameError):
    """Порушення структури кадру або протокольного контракту (чужа адреса, невідомий код)."""
    pass


# ============================================================================
# ТАБЛИЧНИЙ РОЗРАХУНОК CRC-16 (MODBUS RTU)
# ============================================================================

class Crc16Calculator:
    """
    Швидкісний табличний обчислювач циклічної контрольної суми CRC-16 для Modbus RTU.

    Параметри алгоритму:
    - Поліном: 0xA001 (дзеркальний до 0x8005)
    - Початкове значення регістру (Init): 0xFFFF
    - Порядок байтів у кадрі: Little-Endian (спочатку молодший байт, потім старший)
    """

    _TABLE: tuple[int, ...] = ()

    @classmethod
    def _init_table(cls) -> tuple[int, ...]:
        """Генерує таблицю передрозрахованих 16-бітних значень для 256 байтів."""
        table = []
        for byte in range(256):
            crc = byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
            table.append(crc & 0xFFFF)
        return tuple(table)

    @classmethod
    def compute(cls, data: bytes) -> int:
        """
        Обчислює 16-бітну контрольну суму для послідовності байтів.

        :param data: Потік байтів запиту або відповіді без байтів контрольної суми.
        :return: 16-бітне ціле число (0..0xFFFF).
        """
        if not cls._TABLE:
            cls._TABLE = cls._init_table()

        crc = 0xFFFF
        table = cls._TABLE
        for b in data:
            crc = (crc >> 8) ^ table[(crc ^ b) & 0xFF]
        return crc & 0xFFFF

    @classmethod
    def append_crc(cls, payload: bytes) -> bytes:
        """
        Додає 2 байти CRC-16 у форматі Little-Endian до корисного навантаження кадру.
        """
        crc = cls.compute(payload)
        return payload + struct.pack("<H", crc)

    @classmethod
    def verify(cls, frame: bytes) -> bool:
        """
        Перевіряє цілісність отриманого кадру, порівнюючи обчислену CRC
        із переданою у двох останніх байтах.

        :param frame: Повний двійковий кадр, що містить як мінімум 2 байти CRC.
        :return: True, якщо контрольна сума збігається; False у протилежному випадку.
        """
        if len(frame) < 3:
            return False
        payload = frame[:-2]
        expected_crc = struct.unpack("<H", frame[-2:])[0]
        return cls.compute(payload) == expected_crc


# ============================================================================
# СТРУКТУРА ТА РОЗБІР КАДРІВ MODBUS RTU
# ============================================================================

@dataclass(frozen=True)
class ModbusResponse:
    """
    Результат розбору двійкового кадру відповіді веденого пристрою.
    """

    slave_id: int
    function_code: int
    is_exception: bool
    exception_code: Optional[int] = None
    register_address: Optional[int] = None
    register_value: Optional[int] = None


class ModbusFrame:
    """
    Пакувальник та валідатор двійкових кадрів Modbus RTU.

    Інкапсулює бінарне представлення запитів запису одиночного регістра
    (функція 0x06) та декодування нормальних відповідей і протокольних кодів винятків.
    """

    FUNCTION_WRITE_SINGLE_REGISTER: int = 0x06

    # Стандартні коди протокольних винятків Modbus
    EX_ILLEGAL_FUNCTION: int = 0x01
    EX_ILLEGAL_DATA_ADDRESS: int = 0x02
    EX_ILLEGAL_DATA_VALUE: int = 0x03
    EX_SLAVE_DEVICE_FAILURE: int = 0x04

    @classmethod
    def build_write_single_register(
        cls, slave_id: int, register_address: int, value: int
    ) -> bytes:
        """
        Формує повний бінарний кадр Modbus RTU запиту запису одного 16-бітного регістра.

        Структура кадру (8 байтів):
        - Байт 0: Адреса веденого вузла (Slave Address, 1..247)
        - Байт 1: Код функції (0x06 - Write Single Register)
        - Байти 2..3: Адреса регістра у форматі Big-Endian
        - Байти 4..5: 16-бітне значення у форматі Big-Endian
        - Байти 6..7: Контрольна сума CRC-16 у форматі Little-Endian

        :param slave_id: Адреса цільового актуатора на шині RS-485 (1..247).
        :param register_address: Номер цільового регістра утримання (0..65535).
        :param value: 16-бітне цілочисельне значення уставки (0..65535).
        :return: 8-байтний двійковий масив, готовий до відправки в послідовний порт.
        """
        if not (1 <= slave_id <= 247):
            raise ValueError(f"Неприпустима адреса Slave ID [1..247]: {slave_id}")
        if not (0 <= register_address <= 0xFFFF):
            raise ValueError(f"Адреса регістра виходить за 16-бітний діапазон: {register_address}")
        if not (0 <= value <= 0xFFFF):
            raise ValueError(f"Значення уставки виходить за 16-бітний діапазон: {value}")

        payload = struct.pack(
            ">BBHH",
            slave_id,
            cls.FUNCTION_WRITE_SINGLE_REGISTER,
            register_address,
            value,
        )
        return Crc16Calculator.append_crc(payload)

    @classmethod
    def parse_response(
        cls, raw_bytes: bytes, expected_slave_id: int, expected_function_code: int = 0x06
    ) -> ModbusResponse:
        """
        Здійснює валідацію та розбір отриманого з лінії зв'язку двійкового пакета.

        :param raw_bytes: Сирий потік байтів відповіді пристрою.
        :param expected_slave_id: Очікувана адреса веденого вузла.
        :param expected_function_code: Очікуваний код функції запиту (за замовчуванням 0x06).
        :return: Типізований об'єкт ModbusResponse.
        :raises ModbusFrameError: Якщо кадр надто короткий.
        :raises ModbusCrcError: Якщо контрольна сума спотворена.
        :raises ModbusProtocolViolation: Якщо не збігається Slave ID або код функції.
        """
        if len(raw_bytes) < 5:
            raise ModbusFrameError(
                f"Кадр занадто короткий для Modbus RTU: отримано {len(raw_bytes)} байтів (мін. 5)"
            )

        if not Crc16Calculator.verify(raw_bytes):
            raise ModbusCrcError("Помилка контрольної суми CRC-16: пакет спотворено завадами")

        slave_id = raw_bytes[0]
        if slave_id != expected_slave_id:
            raise ModbusProtocolViolation(
                f"Невідповідність адреси веденого: очікувалася {expected_slave_id}, отримано {slave_id}"
            )

        function_code = raw_bytes[1]

        # Перевірка на кадр винятку (старший біт коду функції встановлено в 1)
        exception_function_code = expected_function_code | 0x80
        if function_code == exception_function_code:
            exception_code = raw_bytes[2]
            return ModbusResponse(
                slave_id=slave_id,
                function_code=function_code,
                is_exception=True,
                exception_code=exception_code,
            )

        # Перевірка штатної відповіді відлуння (Echo response для функції 0x06)
        if function_code == expected_function_code:
            if len(raw_bytes) != 8:
                raise ModbusFrameError(
                    f"Некоректна довжина штатної відповіді функції {hex(function_code)}: "
                    f"очікувалося 8 байтів, отримано {len(raw_bytes)}"
                )
            reg_addr, reg_val = struct.unpack(">HH", raw_bytes[2:6])
            return ModbusResponse(
                slave_id=slave_id,
                function_code=function_code,
                is_exception=False,
                register_address=reg_addr,
                register_value=reg_val,
            )

        raise ModbusProtocolViolation(
            f"Неочікуваний код функції у відповіді: {hex(function_code)} "
            f"(очікувався {hex(expected_function_code)} або {hex(exception_function_code)})"
        )
