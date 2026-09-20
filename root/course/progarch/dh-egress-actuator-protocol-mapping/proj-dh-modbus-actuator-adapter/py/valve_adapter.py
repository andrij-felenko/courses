"""
Вихідний адаптер керування опалювальним клапаном (ModbusHeatingValveAdapter).

Реалізує гексагональний контракт HeatingValveActuatorPort:
- Антикорупційний шар (ACL) масштабування відсотка у 16-бітний регістр із насиченням (clamping);
- Арбітраж напівдуплексної шини RS-485 через асинхронне блокування asyncio.Lock;
- Витримування захисної міжфреймової паузи t3.5;
- Контроль таймаутів очікування відповіді актуатора;
- Політику повторних спроб (retries) лише при спотворенні CRC;
- Трансляцію апаратних винятків Modbus у типізований результат Result без протікання винятків.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional, Protocol

from domain import (
    ActuatorError,
    ActuatorHardwareFault,
    ActuatorProtocolError,
    ActuatorUnresponsive,
    HeatingValveActuatorPort,
    Result,
    ValvePosition,
)
from modbus_rtu import (
    ModbusCrcError,
    ModbusFrame,
    ModbusFrameError,
    ModbusProtocolViolation,
)


class RS485Bus(Protocol):
    """
    Протокол асинхронного транспорту напівдуплексної шини RS-485.

    Абстрагує низькорівневу взаємодію з послідовним портом або емулятором шини.
    """

    async def transact(self, request: bytes, timeout: float) -> bytes:
        """
        Передати кадр запиту у лінію та прийняти відповідь веденого вузла.

        :param request: Двійковий кадр запиту.
        :param timeout: Граничний час очікування відповіді у секундах.
        :return: Двійковий кадр відповіді пристрою.
        :raises asyncio.TimeoutError: Якщо пристрій не відповів за timeout.
        :raises IOError: При апаратному обриві лінії або помилці драйвера порту.
        """
        ...


class ModbusHeatingValveAdapter(HeatingValveActuatorPort):
    """
    Вихідний адаптер (Driven Adapter) приводу опалювального клапана через Modbus RTU.

    З'єднує чистий доменний світ із фізичною периферією:
    - Захищає ядро від знання адрес регістрів і специфіки Modbus;
    - Ізолює монопольний доступ до лінії RS-485 між конкуруючими корутинами;
    - Гарантує повернення детермінованого Result замість викиду необроблених помилок введення-виведення.
    """

    # Межі 16-бітного регістра утримання актуатора Digital Homes
    REGISTER_MIN_VAL: int = 0
    REGISTER_MAX_VAL: int = 10000
    SCALE_FACTOR: float = 100.0  # 100.0% -> 10000 відліків

    def __init__(
        self,
        bus: RS485Bus,
        slave_id: int = 1,
        register_address: int = 0x0001,
        timeout_sec: float = 1.0,
        max_retries: int = 2,
        inter_frame_delay_sec: float = 0.002,
    ) -> None:
        """
        Ініціалізує вихідний адаптер клапана.

        :param bus: Транспорт послідовної шини RS-485.
        :param slave_id: Фізична адреса актуатора на шині Modbus (1..247).
        :param register_address: Зміщення 16-бітного регістра уставки позиції.
        :param timeout_sec: Максимальний час очікування відповіді актуатора.
        :param max_retries: Кількість повторних спроб при спотворенні CRC.
        :param inter_frame_delay_sec: Захисна міжфреймова пауза тиші t3.5 (~1.75..2.0 мс).
        """
        self._bus = bus
        self._slave_id = slave_id
        self._register_address = register_address
        self._timeout_sec = timeout_sec
        self._max_retries = max_retries
        self._inter_frame_delay_sec = inter_frame_delay_sec

        # Асинхронний м'ютекс для арбітражу напівдуплексної шини RS-485
        self._lock = asyncio.Lock()

    # ========================================================================
    # АНТИКОРУПЦІЙНИЙ ШАР (ACL): МАСШТАБУВАННЯ З НАСИЧЕННЯМ (CLAMPING)
    # ========================================================================

    def _scale_position_to_register(self, position: ValvePosition) -> int:
        """
        Транслює доменний відсоток у 16-бітне ціле число регістра з насиченням меж.

        Арифметика насичення (saturation / clamping) гарантує, що через похибки
        округлення з плаваючою крапкою значення ніколи не перевищить діапазон [0..10000],
        запобігаючи переповненню розрядної сітки контролера клапана.
        """
        raw_val = round(position.percent * self.SCALE_FACTOR)
        clamped_val = max(self.REGISTER_MIN_VAL, min(self.REGISTER_MAX_VAL, int(raw_val)))
        return clamped_val

    # ========================================================================
    # РЕАЛІЗАЦІЯ ПОРТУ: КОНВЕЄР НАДСИЛАННЯ ТА ОБРОБКИ ПОМИЛОК
    # ========================================================================

    async def set_position(self, position: ValvePosition) -> Result[None, ActuatorError]:
        """
        Асинхронно відправляє команду позиціонування клапана через Modbus RTU.

        Конкурентні виклики цієї корутини безпечно впорядковуються за допомогою
        asyncio.Lock. Пристрій захищено від електричних колізій на спільній шині.
        """
        # 1. Антикорупційний шар: трансляція позиції у значення регістра
        register_value = self._scale_position_to_register(position)

        # 2. Формування двійкового кадру Modbus RTU (функція 0x06)
        try:
            request_frame = ModbusFrame.build_write_single_register(
                slave_id=self._slave_id,
                register_address=self._register_address,
                value=register_value,
            )
        except ValueError as ex:
            return Result.err(
                ActuatorProtocolError(f"Помилка формування кадру Modbus: {ex}")
            )

        # 3. Арбітраж шини та захищена транзакція під м'ютексом
        async with self._lock:
            return await self._execute_with_retries(request_frame, register_value)

    async def _execute_with_retries(
        self, request_frame: bytes, expected_value: int
    ) -> Result[None, ActuatorError]:
        """
        Виконує транзакцію на шині RS-485 із контролем таймауту та політикою retries.

        Повторні спроби виконуються виключно при збоях контрольної суми CRC-16
        (за збереження ідемпотентності абсолютного запису уставки).
        При апаратних збоях або таймауті повтори не виконуються для запобігання каскадним затримкам.
        """
        attempts = self._max_retries + 1

        for attempt in range(1, attempts + 1):
            # Захисна нормативна пауза тиші t3.5 перед початком передачі кадру
            if self._inter_frame_delay_sec > 0:
                await asyncio.sleep(self._inter_frame_delay_sec)

            try:
                # Відправка кадру з жорстким контролем таймауту
                response_bytes = await self._bus.transact(
                    request_frame, timeout=self._timeout_sec
                )
            except (asyncio.TimeoutError, TimeoutError):
                return Result.err(
                    ActuatorUnresponsive(
                        f"Актуатор (Slave ID {self._slave_id}) не відповів за {self._timeout_sec}с "
                        f"(таймаут шини RS-485)"
                    )
                )
            except IOError as ex:
                return Result.err(
                    ActuatorHardwareFault(
                        f"Апаратний збій каналу зв'язку RS-485: {ex}"
                    )
                )
            except Exception as ex:
                return Result.err(
                    ActuatorHardwareFault(
                        f"Непередбачений збій введення-виведення на шині: {ex}"
                    )
                )

            # Розбір отриманого двійкового кадру
            try:
                response = ModbusFrame.parse_response(
                    raw_bytes=response_bytes,
                    expected_slave_id=self._slave_id,
                    expected_function_code=ModbusFrame.FUNCTION_WRITE_SINGLE_REGISTER,
                )
            except ModbusCrcError as crc_err:
                # При спотворенні CRC виконуємо повторну спробу, якщо ліміт не вичерпано
                if attempt < attempts:
                    continue
                return Result.err(
                    ActuatorProtocolError(
                        f"Вичерпано спроби надсилання: спотворення CRC-16 кадру відповіді "
                        f"після {attempts} спроб ({crc_err})"
                    )
                )
            except (ModbusFrameError, ModbusProtocolViolation) as frame_err:
                return Result.err(
                    ActuatorProtocolError(
                        f"Протокольне порушення у відповіді актуатора: {frame_err}"
                    )
                )

            # Обробка протокольних кодів винятків Modbus
            if response.is_exception:
                return self._map_modbus_exception(response.exception_code)

            # Перевірка ехо-відповіді: актуатор повинен підтвердити адресу та записане значення
            if (
                response.register_address != self._register_address
                or response.register_value != expected_value
            ):
                return Result.err(
                    ActuatorProtocolError(
                        f"Розбіжність ехо-відповіді: записано ({self._register_address}={expected_value}), "
                        f"підтверджено ({response.register_address}={response.register_value})"
                    )
                )

            # Успішне підтвердження запису уставки
            return Result.ok(None)

        return Result.err(
            ActuatorProtocolError("Транзакцію не вдалося завершити через вичерпання спроб")
        )

    def _map_modbus_exception(self, exception_code: Optional[int]) -> Result[None, ActuatorError]:
        """
        Транслює числовий код протокольного винятку Modbus у типізовану доменну помилку.
        """
        if exception_code == ModbusFrame.EX_SLAVE_DEVICE_FAILURE:
            return Result.err(
                ActuatorHardwareFault(
                    f"Аварійний стан приводу клапана: помилка Modbus 0x04 (Slave Device Failure)"
                )
            )
        elif exception_code == ModbusFrame.EX_ILLEGAL_DATA_ADDRESS:
            return Result.err(
                ActuatorProtocolError(
                    f"Неприпустима адреса регістра {self._register_address}: "
                    f"помилка Modbus 0x02 (Illegal Data Address)"
                )
            )
        elif exception_code == ModbusFrame.EX_ILLEGAL_FUNCTION:
            return Result.err(
                ActuatorProtocolError(
                    f"Непідтримувана функція запису: помилка Modbus 0x01 (Illegal Function)"
                )
            )
        elif exception_code == ModbusFrame.EX_ILLEGAL_DATA_VALUE:
            return Result.err(
                ActuatorProtocolError(
                    f"Значення уставки відхилено приводом: помилка Modbus 0x03 (Illegal Data Value)"
                )
            )
        else:
            return Result.err(
                ActuatorProtocolError(
                    f"Отримано невідомий протокольний код винятку Modbus: {exception_code}"
                )
            )
