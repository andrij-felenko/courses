"""
Модульні тести та верифікаційний стенд вихідного адаптера Modbus RTU.

Містить:
- MockRS485Bus: програмний емулятор напівдуплексної шини RS-485 та веденого актуатора;
- Модульні тести для перевірки квантування ACL, розрахунку CRC-16,
  арбітражу шини м'ютексом при конкурентних викликах, контролю таймаутів
  та мапінгу виняткових ситуацій у типізовані доменні помилки Result.
"""

from __future__ import annotations

import asyncio
import math
import struct
import unittest

from domain import (
    ActuatorError,
    ActuatorHardwareFault,
    ActuatorProtocolError,
    ActuatorUnresponsive,
    HeatingValveActuatorPort,
    Result,
    ValvePosition,
)
from modbus_rtu import Crc16Calculator, ModbusCrcError, ModbusFrame
from valve_adapter import ModbusHeatingValveAdapter


# ============================================================================
# ТЕСТОВИЙ ДУБЛЕР: ПРОГРАМНИЙ ЕМУЛЯТОР ШИНИ RS-485 ТА КЛАПАНА MODBUS
# ============================================================================

class MockRS485Bus:
    """
    Програмний емулятор напівдуплексної послідовної шини RS-485 і веденого пристрою.

    Симулює фізичні властивості лінії:
    - Контроль одночасного доступу: детектує електричні колізії, якщо два запити
      надходять одночасно без блокування;
    - Затримку поширення сигналу в середовищі;
    - Апаратні збої: таймаути (обрив лінії), апаратні збої введення-виведення,
      спотворення CRC-16 завадами та протокольні винятки Modbus (0x01, 0x02, 0x04).
    """

    def __init__(
        self,
        slave_id: int = 1,
        transmission_delay_sec: float = 0.005,
    ) -> None:
        self.slave_id = slave_id
        self.transmission_delay_sec = transmission_delay_sec
        self.registers: dict[int, int] = {0x0001: 0}

        # Прапорці детекції та моделювання аномалій
        self.simulate_timeout: bool = False
        self.simulate_io_error: bool = False
        self.simulate_exception_code: int | None = None
        self.corrupt_crc_count: int = 0
        self.always_corrupt_crc: bool = False

        # Моніторинг монопольності шини та кількості транзакцій
        self.active_transmissions: int = 0
        self.collision_detected: bool = False
        self.transaction_count: int = 0

    async def transact(self, request: bytes, timeout: float) -> bytes:
        """
        Симулює передачу кадру запиту та отримання відповіді на шині RS-485.
        """
        # Детекція колізій: напівдуплексна шина допускає лише один активний сигнал
        self.active_transmissions += 1
        if self.active_transmissions > 1:
            self.collision_detected = True

        try:
            self.transaction_count += 1

            # Симуляція апаратного збою фізичного трансивера RS-485
            if self.simulate_io_error:
                raise IOError("Апаратна помилка шини RS-485: обрив диференціальної пари")

            # Симуляція таймауту (мовчання веденого клапана)
            if self.simulate_timeout:
                await asyncio.sleep(timeout + 0.05)
                raise asyncio.TimeoutError("Таймаут шини RS-485")

            # Затримка передачі сигналу по лінії
            if self.transmission_delay_sec > 0:
                await asyncio.sleep(self.transmission_delay_sec)

            # Валідація CRC отриманого запиту від адаптера (Master)
            if not Crc16Calculator.verify(request):
                raise ModbusCrcError("Кадр запиту від ведучого містить биту контрольну суму")

            slave_id, func, addr, val = struct.unpack(">BBHH", request[:6])

            # Ведений вузол ігнорує кадри, адресовані іншим пристроям на спільній шині
            if slave_id != self.slave_id:
                await asyncio.sleep(timeout + 0.05)
                raise asyncio.TimeoutError("Пристрій ігнорує чужу адресу Slave ID")

            # Симуляція протокольних винятків Modbus
            if self.simulate_exception_code is not None:
                ex_payload = struct.pack(
                    ">BBB", slave_id, func | 0x80, self.simulate_exception_code
                )
                return Crc16Calculator.append_crc(ex_payload)

            # Штатна обробка функції 0x06 (Write Single Register)
            if func == ModbusFrame.FUNCTION_WRITE_SINGLE_REGISTER:
                self.registers[addr] = val
                response_payload = request[:6]  # Стандартне відлуння (Echo)
                response = Crc16Calculator.append_crc(response_payload)
            else:
                # Непідтримувана функція (0x01 Illegal Function)
                ex_payload = struct.pack(
                    ">BBB", slave_id, func | 0x80, ModbusFrame.EX_ILLEGAL_FUNCTION
                )
                return Crc16Calculator.append_crc(ex_payload)

            # Симуляція пошкодження контрольної суми CRC завадами в лінії
            if self.always_corrupt_crc or self.corrupt_crc_count > 0:
                if self.corrupt_crc_count > 0:
                    self.corrupt_crc_count -= 1
                corrupted = bytearray(response)
                corrupted[-1] ^= 0xFF  # Інверсія бітів контрольної суми
                return bytes(corrupted)

            return response
        finally:
            self.active_transmissions -= 1


# ============================================================================
# НАБІР МОДУЛЬНИХ ТЕСТІВ
# ============================================================================

class TestHeatingValveAdapter(unittest.IsolatedAsyncioTestCase):
    """
    Тестовий набір для повної верифікації вихідного адаптера опалювального клапана.
    """

    async def asyncSetUp(self) -> None:
        self.bus = MockRS485Bus(slave_id=1, transmission_delay_sec=0.002)
        self.adapter = ModbusHeatingValveAdapter(
            bus=self.bus,
            slave_id=1,
            register_address=0x0001,
            timeout_sec=0.1,
            max_retries=2,
            inter_frame_delay_sec=0.001,
        )

    # ------------------------------------------------------------------------
    # ТЕСТИ ДОМЕННИХ ІНВАРІАНТІВ
    # ------------------------------------------------------------------------

    def test_valve_position_domain_invariants(self) -> None:
        """Перевірка забезпечення інваріантів Value Object ValvePosition."""
        # Валідні граничні та проміжні значення
        self.assertEqual(ValvePosition(0.0).percent, 0.0)
        self.assertEqual(ValvePosition(50.0).percent, 50.0)
        self.assertEqual(ValvePosition(100.0).percent, 100.0)
        self.assertEqual(ValvePosition.closed().percent, 0.0)
        self.assertEqual(ValvePosition.fully_open().percent, 100.0)

        # Невалідні значення викликають ValueError
        with self.assertRaises(ValueError):
            ValvePosition(-0.1)
        with self.assertRaises(ValueError):
            ValvePosition(100.05)
        with self.assertRaises(ValueError):
            ValvePosition(float("nan"))
        with self.assertRaises(ValueError):
            ValvePosition(float("inf"))

    # ------------------------------------------------------------------------
    # ТЕСТИ АНТИКОРУПЦІЙНОГО ШАРУ (ACL)
    # ------------------------------------------------------------------------

    def test_acl_scaling_and_saturation_clamping(self) -> None:
        """Перевірка масштабування відсотка у 16-бітний регістр із насиченням."""
        # Пряме масштабування
        self.assertEqual(
            self.adapter._scale_position_to_register(ValvePosition(0.0)), 0
        )
        self.assertEqual(
            self.adapter._scale_position_to_register(ValvePosition(25.5)), 2550
        )
        self.assertEqual(
            self.adapter._scale_position_to_register(ValvePosition(50.0)), 5000
        )
        self.assertEqual(
            self.adapter._scale_position_to_register(ValvePosition(99.99)), 9999
        )
        self.assertEqual(
            self.adapter._scale_position_to_register(ValvePosition(100.0)), 10000
        )

    # ------------------------------------------------------------------------
    # ТЕСТИ КОНТРОЛЬНОЇ СУМИ CRC-16
    # ------------------------------------------------------------------------

    def test_crc16_calculation_and_verification(self) -> None:
        """Верифікація табличного розрахунку CRC-16 за еталонними векторами Modbus."""
        # Еталонний кадр Modbus: Slave=1, Func=3, Start=0, Count=10 -> CRC: 0xC5CD (LE: C5 CD)
        test_payload = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x0A])
        computed_crc = Crc16Calculator.compute(test_payload)
        self.assertEqual(computed_crc, 0xCDC5)

        frame_with_crc = Crc16Calculator.append_crc(test_payload)
        self.assertEqual(len(frame_with_crc), len(test_payload) + 2)
        self.assertTrue(Crc16Calculator.verify(frame_with_crc))

        # Спотворення навіть одного біта повинно ламати перевірку
        corrupted_frame = bytearray(frame_with_crc)
        corrupted_frame[2] ^= 0x01
        self.assertFalse(Crc16Calculator.verify(bytes(corrupted_frame)))

    # ------------------------------------------------------------------------
    # ТЕСТИ ШТАТНОГО ПОЗИЦІОНУВАННЯ КЛАПАНА
    # ------------------------------------------------------------------------

    async def test_successful_position_command(self) -> None:
        """Перевірка успішного позиціонування клапана через адаптер."""
        result = await self.adapter.set_position(ValvePosition(73.5))

        self.assertTrue(result.is_ok)
        self.assertIsNone(result.unwrap())
        # Перевірка фактичного запису в регістр веденого пристрою
        self.assertEqual(self.bus.registers[0x0001], 7350)
        self.assertFalse(self.bus.collision_detected)

    # ------------------------------------------------------------------------
    # ТЕСТИ АРБІТРАЖУ ШИНИ RS-485 (КОНКУРЕНТНІ ВИКЛИКИ)
    # ------------------------------------------------------------------------

    async def test_concurrent_calls_arbitration_without_collisions(self) -> None:
        """
        Перевірка взаємного виключення доступу до лінії: конкурентні корутини
        серіалізуються через asyncio.Lock без електричних колізій на шині.
        """
        positions = [
            ValvePosition(10.0),
            ValvePosition(20.0),
            ValvePosition(30.0),
            ValvePosition(40.0),
            ValvePosition(50.0),
        ]

        # Одночасний запуск 5 конкурентних операцій позиціонування
        tasks = [self.adapter.set_position(pos) for pos in positions]
        results = await asyncio.gather(*tasks)

        # Усі операції повинні успішно завершитися
        for res in results:
            self.assertTrue(res.is_ok)

        # Головний інваріант арбітражу: колізій на шині не виникло
        self.assertFalse(self.bus.collision_detected)
        self.assertEqual(self.bus.transaction_count, len(positions))
        # Останнє записане значення у регістрі має відповідати одній із уставок
        self.assertIn(self.bus.registers[0x0001], [1000, 2000, 3000, 4000, 5000])

    # ------------------------------------------------------------------------
    # ТЕСТИ ТРАНСЛЯЦІЇ ТАЙМАУТІВ ТА АППАРАТНИХ ЗБОЇВ
    # ------------------------------------------------------------------------

    async def test_bus_timeout_translates_to_actuator_unresponsive(self) -> None:
        """Перевірка відображення таймауту зв'язку у доменну помилку ActuatorUnresponsive."""
        self.bus.simulate_timeout = True

        result = await self.adapter.set_position(ValvePosition(40.0))

        self.assertTrue(result.is_err)
        error = result.unwrap_err()
        self.assertIsInstance(error, ActuatorUnresponsive)
        self.assertIn("таймаут", error.message.lower())

    async def test_modbus_exception_0x04_translates_to_hardware_fault(self) -> None:
        """Перевірка мапінгу протокольного коду 0x04 у ActuatorHardwareFault."""
        self.bus.simulate_exception_code = ModbusFrame.EX_SLAVE_DEVICE_FAILURE

        result = await self.adapter.set_position(ValvePosition(80.0))

        self.assertTrue(result.is_err)
        error = result.unwrap_err()
        self.assertIsInstance(error, ActuatorHardwareFault)
        self.assertIn("0x04", error.message)

    async def test_modbus_exception_0x02_translates_to_protocol_error(self) -> None:
        """Перевірка мапінгу некоректної адреси регістра 0x02 у ActuatorProtocolError."""
        self.bus.simulate_exception_code = ModbusFrame.EX_ILLEGAL_DATA_ADDRESS

        result = await self.adapter.set_position(ValvePosition(15.0))

        self.assertTrue(result.is_err)
        error = result.unwrap_err()
        self.assertIsInstance(error, ActuatorProtocolError)
        self.assertIn("0x02", error.message)

    async def test_io_error_translates_to_hardware_fault(self) -> None:
        """Перевірка обробки фізичного обриву лінії RS-485."""
        self.bus.simulate_io_error = True

        result = await self.adapter.set_position(ValvePosition(60.0))

        self.assertTrue(result.is_err)
        error = result.unwrap_err()
        self.assertIsInstance(error, ActuatorHardwareFault)
        self.assertIn("обрив", error.message.lower())

    # ------------------------------------------------------------------------
    # ТЕСТИ ПОЛІТИКИ ПОВТОРНИХ СПРОБ (RETRIES) ДЛЯ CRC
    # ------------------------------------------------------------------------

    async def test_transient_crc_error_recovers_via_retry(self) -> None:
        """
        Перевірка відновлення при короткочасній заваді: перша спроба повертає
        биту CRC, але повторна спроба (retry) успішно застосовує уставку.
        """
        self.bus.corrupt_crc_count = 1  # Спотворити рівно одну відповідь

        result = await self.adapter.set_position(ValvePosition(65.0))

        self.assertTrue(result.is_ok)
        self.assertEqual(self.bus.registers[0x0001], 6500)
        # Мало бути виконано рівно дві транзакції: збійна та повторна
        self.assertEqual(self.bus.transaction_count, 2)

    async def test_persistent_crc_error_exhausts_retries_and_fails(self) -> None:
        """
        Перевірка вичерпання ліміту спроб при стійкому спотворенні лінії:
        після max_retries повертається ActuatorProtocolError.
        """
        self.bus.always_corrupt_crc = True

        result = await self.adapter.set_position(ValvePosition(90.0))

        self.assertTrue(result.is_err)
        error = result.unwrap_err()
        self.assertIsInstance(error, ActuatorProtocolError)
        self.assertIn("crc-16", error.message.lower())
        # Було виконано 1 основну + 2 повторні спроби (разом 3)
        self.assertEqual(self.bus.transaction_count, 3)


if __name__ == "__main__":
    unittest.main()
