"""Пасивне сканування BLE через сирий HCI-сокет ядра Linux.

Давачі на рухомих підшипниках не тримають з'єднання: прокинувся, кинув
рекламний кадр, заснув. Тому ніякого GATT тут немає — лише розбір реклами.

Потрібні CAP_NET_RAW (відкрити сокет) і CAP_NET_ADMIN (віддати контролеру
команду сканування); bluetoothd на цьому ж адаптері сканувати одночасно не
повинен — він перезапише параметри.
"""

from __future__ import annotations

import asyncio
import socket
import struct
from dataclasses import dataclass

HCI_COMMAND_PKT = 0x01
HCI_EVENT_PKT = 0x04
EVT_CMD_COMPLETE = 0x0E
EVT_LE_META = 0x3E
LE_ADVERTISING_REPORT = 0x02

SOL_HCI = 0
HCI_FILTER = 2

# OGF 0x08 (LE Controller) → opcode = (OGF << 10) | OCF
OP_LE_SET_SCAN_PARAMS = 0x200B
OP_LE_SET_SCAN_ENABLE = 0x200C

AD_SERVICE_DATA_16 = 0x16  # Service Data з 16-бітним UUID
UUID_ENV_SENSING = 0x181A  # Environmental Sensing Service
SENSOR_FORMAT_V1 = 0x01  # версія формату, int16 сотих градуса, заряд у відсотках


class BleError(Exception):
    """Сканування не піднялося або відвалилося."""


@dataclass(frozen=True, slots=True)
class BleSample:
    address: bytes  # як у HCI, молодшим байтом уперед
    temperature_c: float
    battery_pct: int
    rssi_dbm: int

    @property
    def address_text(self) -> str:
        return ":".join(f"{byte:02X}" for byte in reversed(self.address))


def parse_advertising_data(data: bytes) -> tuple[float, int] | None:
    """Розбір поля реклами: послідовність структур «довжина, тип, вміст»."""
    offset = 0
    while offset < len(data):
        length = data[offset]
        if length == 0:
            break  # нульова довжина — далі лише набивка
        if offset + 1 + length > len(data):
            return None  # кадр обрізаний, довіряти йому не можна

        ad_type = data[offset + 1]
        body = data[offset + 2:offset + 1 + length]
        if ad_type == AD_SERVICE_DATA_16 and len(body) >= 6:
            uuid, fmt, centi, battery = struct.unpack("<HBhB", body[:6])
            if uuid == UUID_ENV_SENSING and fmt == SENSOR_FORMAT_V1:
                return centi / 100.0, battery
        offset += 1 + length
    return None


class BleScanner:
    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    @classmethod
    async def start(cls, hci_index: int = 0) -> BleScanner:
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        try:
            sock.bind((hci_index,))
            sock.setblocking(False)
            # Пропускаємо всі події й відсіюємо потрібні самі: розбір усе одно
            # зосереджено в одному місці, фільтр ядра тут нічого не заощадив би.
            sock.setsockopt(SOL_HCI, HCI_FILTER,
                            struct.pack("<IIIH", 1 << HCI_EVENT_PKT, 0xFFFFFFFF, 0xFFFFFFFF, 0))

            scanner = cls(sock)
            # Скидаємо можливе попереднє сканування, інакше зміна параметрів
            # відхиляється з Command Disallowed.
            try:
                await scanner._set_scan_enable(False)
            except BleError:
                pass  # контролер і так не сканував

            await scanner._command(OP_LE_SET_SCAN_PARAMS, bytes([
                0x00,        # пасивне сканування: SCAN_REQ не шлемо, ефір не гріємо
                0xA0, 0x00,  # інтервал 0x00A0 × 0.625 мс = 100 мс
                0xA0, 0x00,  # вікно дорівнює інтервалу — слухаємо безперервно
                0x00,        # власна адреса публічна
                0x00,        # приймати від усіх, білого списку немає
            ]))
            await scanner._set_scan_enable(True)
            return scanner
        except Exception:
            sock.close()
            raise

    async def close(self) -> None:
        try:
            # Радіо, забуте ввімкненим, їсть акумулятор шлюза цілодобово.
            await self._set_scan_enable(False)
        except (BleError, OSError):
            pass
        finally:
            self._sock.close()

    async def __aenter__(self) -> BleScanner:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    async def _command(self, opcode: int, params: bytes) -> None:
        loop = asyncio.get_running_loop()
        packet = struct.pack("<BHB", HCI_COMMAND_PKT, opcode, len(params)) + params
        await loop.sock_sendall(self._sock, packet)

        # Без Command Complete ми не знаємо, чи контролер узагалі почав сканувати.
        deadline = loop.time() + 2.0
        while loop.time() < deadline:
            try:
                event = await asyncio.wait_for(loop.sock_recv(self._sock, 260), deadline - loop.time())
            except asyncio.TimeoutError:
                break
            if len(event) < 7 or event[0] != HCI_EVENT_PKT or event[1] != EVT_CMD_COMPLETE:
                continue
            if struct.unpack("<H", event[4:6])[0] != opcode:
                continue
            if event[6] != 0x00:
                raise BleError(f"контролер відхилив команду 0x{opcode:04X}, статус 0x{event[6]:02X}")
            return
        raise BleError(f"контролер не підтвердив команду 0x{opcode:04X}")

    async def _set_scan_enable(self, enable: bool) -> None:
        # Другий байт — фільтр дублів: без нього один давач засипле нас копіями.
        await self._command(OP_LE_SET_SCAN_ENABLE, bytes([0x01 if enable else 0x00, 0x01]))

    async def next_sample(self, timeout: float = 0.5) -> BleSample | None:
        loop = asyncio.get_running_loop()
        try:
            event = await asyncio.wait_for(loop.sock_recv(self._sock, 260), timeout)
        except asyncio.TimeoutError:
            return None
        except OSError as error:
            raise BleError(f"сокет HCI помер: {error}") from error
        if not event:
            raise BleError("сокет HCI закрився")

        # Подія HCI: [тип пакета][код події][довжина][параметри]
        if len(event) < 5 or event[0] != HCI_EVENT_PKT or event[1] != EVT_LE_META:
            return None
        if event[3] != LE_ADVERTISING_REPORT:
            return None

        offset = 5
        for _ in range(event[4]):
            # Звіт: тип події(1), тип адреси(1), адреса(6), довжина(1), дані, RSSI(1)
            if offset + 9 > len(event):
                return None
            data_length = event[offset + 8]
            if offset + 9 + data_length + 1 > len(event):
                return None

            parsed = parse_advertising_data(event[offset + 9:offset + 9 + data_length])
            if parsed is not None:
                temperature, battery = parsed
                return BleSample(
                    address=event[offset + 2:offset + 8],
                    temperature_c=temperature,
                    battery_pct=battery,
                    rssi_dbm=struct.unpack("b", event[offset + 9 + data_length:offset + 10 + data_length])[0],
                )
            offset += 9 + data_length + 1
        return None
