"""Майстер Modbus RTU поверх RS-485 без сторонніх бібліотек.

Порт відкривається через ``os.open`` і налаштовується ``termios``; чекання
віддане подієвому циклу, тож опитування шини не блокує ні розбір BLE, ні
відправлення в брокер. Доступ до порту серіалізовано ``asyncio.Lock``: до
тієї самої пари дротів ходять і опитувач, і правило автономії.
"""

from __future__ import annotations

import asyncio
import os
import struct
import termios

FC_READ_HOLDING = 0x03
FC_WRITE_COIL = 0x05


class ModbusError(Exception):
    """Обмін не вдався."""


class ModbusTimeout(ModbusError):
    """Підлеглий мовчить довше за дозволений час."""


class ModbusCrcError(ModbusError):
    """Кадр побився в дорозі — наводка на довгій лінії."""


class ModbusFrameError(ModbusError):
    """Відповів не той адресат або не на ту функцію."""


class ModbusException(ModbusError):
    """Підлеглий відповів кодом винятку Modbus."""

    def __init__(self, code: int) -> None:
        super().__init__(f"виняток Modbus 0x{code:02X}")
        self.code = code


def crc16(data: bytes) -> int:
    """Класичний Modbus CRC-16: поліном 0xA001, початкове значення 0xFFFF."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def regs_to_float(regs: tuple[int, int]) -> float:
    """Пара регістрів → float32 IEEE 754, старше слово першим."""
    return struct.unpack(">f", struct.pack(">HH", regs[0], regs[1]))[0]


class ModbusMaster:
    def __init__(self, device: str, baud: int = 19200, timeout: float = 0.5) -> None:
        self._timeout = timeout
        self._lock = asyncio.Lock()
        self._fd = os.open(device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        try:
            self._configure(baud)
        except Exception:
            os.close(self._fd)
            raise

    def _configure(self, baud: int) -> None:
        speed = getattr(termios, f"B{baud}", None)
        if speed is None:
            raise ModbusError(f"швидкість {baud} не підтримується")

        iflag, oflag, cflag, lflag, _ispeed, _ospeed, cc = termios.tcgetattr(self._fd)
        # 8E1 без керування потоком і без модемних ліній — як велить стандарт RTU.
        cflag &= ~(termios.CSIZE | termios.CSTOPB | termios.PARODD | termios.CRTSCTS)
        cflag |= termios.CS8 | termios.PARENB | termios.CLOCAL | termios.CREAD
        iflag = termios.INPCK  # збій парності ловить апарат, решта обробки зайва
        oflag = 0
        lflag = 0  # сирий режим: ні канонічного вводу, ні ехо
        cc = list(cc)
        cc[termios.VMIN] = 0  # усе чекання робить подієвий цикл
        cc[termios.VTIME] = 0
        termios.tcsetattr(self._fd, termios.TCSANOW, [iflag, oflag, cflag, lflag, speed, speed, cc])

    def close(self) -> None:
        os.close(self._fd)

    async def _wait_readable(self, timeout: float) -> None:
        loop = asyncio.get_running_loop()
        future: asyncio.Future[None] = loop.create_future()
        loop.add_reader(self._fd, lambda: future.done() or future.set_result(None))
        try:
            await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError as error:
            raise ModbusTimeout("підлеглий не відповів") from error
        finally:
            loop.remove_reader(self._fd)

    async def _read_exact(self, count: int, deadline: float) -> bytes:
        """Modbus RTU не позначає кінець кадру — довжину ми знаємо з функції."""
        loop = asyncio.get_running_loop()
        buffer = bytearray()
        while len(buffer) < count:
            left = deadline - loop.time()
            if left <= 0:
                raise ModbusTimeout("підлеглий не відповів")
            await self._wait_readable(left)
            try:
                chunk = os.read(self._fd, count - len(buffer))
            except BlockingIOError:
                continue  # хибне пробудження: байт забрав хтось раніше за нас
            if not chunk:
                # Порожнє читання на послідовному порту: перехідник висмикнули.
                raise ModbusError("порт зник із системи")
            buffer += chunk
        return bytes(buffer)

    async def _transact(self, request: bytes) -> bytes:
        loop = asyncio.get_running_loop()
        frame = request + struct.pack("<H", crc16(request))  # CRC молодшим байтом уперед

        termios.tcflush(self._fd, termios.TCIFLUSH)  # луна попереднього обміну не потрібна
        os.write(self._fd, frame)

        deadline = loop.time() + self._timeout
        response = await self._read_exact(2, deadline)
        if response[0] != request[0]:
            raise ModbusFrameError("відповів не той адресат")

        is_exception = bool(response[1] & 0x80)
        if is_exception:
            response += await self._read_exact(3, deadline)  # код винятку + CRC
        elif response[1] != request[1]:
            raise ModbusFrameError("відповідь не на ту функцію")
        elif response[1] == FC_READ_HOLDING:
            response += await self._read_exact(1, deadline)
            response += await self._read_exact(response[2] + 2, deadline)
        else:
            response += await self._read_exact(6, deadline)  # FC 05 віддає луну запиту

        if crc16(response[:-2]) != struct.unpack("<H", response[-2:])[0]:
            raise ModbusCrcError("CRC відповіді не збігся")
        if is_exception:
            raise ModbusException(response[2])
        return response

    async def read_holding(self, slave: int, start: int, count: int) -> tuple[int, ...]:
        if not 1 <= count <= 125:
            raise ModbusFrameError("за раз читається від 1 до 125 регістрів")

        request = struct.pack(">BBHH", slave, FC_READ_HOLDING, start, count)
        async with self._lock:
            response = await self._transact(request)

        if response[2] != count * 2:
            raise ModbusFrameError("довжина даних не збігається із запитом")
        return struct.unpack(f">{count}H", response[3:3 + count * 2])

    async def write_coil(self, slave: int, address: int, on: bool) -> None:
        # 0xFF00 — увімкнути, 0x0000 — вимкнути; інших значень протокол не знає.
        request = struct.pack(">BBHH", slave, FC_WRITE_COIL, address, 0xFF00 if on else 0x0000)
        async with self._lock:
            response = await self._transact(request)

        # Луна мусить збігтися побайтово — інакше ми не знаємо, що спрацювало.
        if response[2:6] != request[2:6]:
            raise ModbusFrameError("луна запису котушки не збіглася")
