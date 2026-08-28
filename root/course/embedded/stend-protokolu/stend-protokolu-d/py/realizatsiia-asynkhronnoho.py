import asyncio
import random
import struct
from typing import Optional

class FaultInjectorConfig:
    def __init__(self):
        self.drop_prob: float = 0.05            # Ймовірність втрати пакета (0..1)
        self.bitflip_prob: float = 0.03         # Ймовірність спотворення біта
        self.min_delay_ms: float = 5.0          # Мінімальна затримка каналу
        self.max_delay_ms: float = 45.0         # Максимальна затримка каналу
        self.reorder_prob: float = 0.02         # Ймовірність затримки для перестановки
        self.truncate_prob: float = 0.01        # Ймовірність обрізання пакета

class FaultInjectionProxy:
    def __init__(self, config: FaultInjectorConfig):
        self.cfg = config
        self._reorder_buffer: Optional[bytes] = None

    def mutate_packet(self, data: bytes) -> Optional[bytes]:
        """Застосовує правила мутації до вхідного двійкового кадру."""
        if not data:
            return data

        # 1. Перевірка на втрату пакета (Drop)
        if random.random() < self.cfg.drop_prob:
            return None

        packet = bytearray(data)

        # 2. Обрізання пакета (Truncation)
        if len(packet) > 4 and random.random() < self.cfg.truncate_prob:
            cut_point = random.randint(2, len(packet) - 1)
            packet = packet[:cut_point]
            return bytes(packet)

        # 3. Спотворення випадкового біта (Bitflip)
        if random.random() < self.cfg.bitflip_prob:
            byte_idx = random.randint(0, len(packet) - 1)
            bit_idx = random.randint(0, 7)
            packet[byte_idx] ^= (1 << bit_idx)

        return bytes(packet)

    async def forward_stream(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Асинхронно зчитує кадри, застосовує затримки та відправляє адресату."""
        while not reader.at_eof():
            try:
                # Зчитуємо сирий блок даних із сокета
                data = await reader.read(512)
                if not data:
                    break

                mutated = self.mutate_packet(data)
                if mutated is None:
                    # Пакет втрачено в каналі
                    continue

                # Розрахунок випадкової затримки каналу (Jitter)
                delay_sec = random.uniform(self.cfg.min_delay_ms, self.cfg.max_delay_ms) / 1000.0

                # Моделювання перестановки (Reordering)
                if random.random() < self.cfg.reorder_prob and self._reorder_buffer is None:
                    self._reorder_buffer = mutated
                    continue

                await asyncio.sleep(delay_sec)
                writer.write(mutated)
                await writer.drain()

                # Якщо є відкладений пакет для перестановки — відправляємо його слідом
                if self._reorder_buffer is not None:
                    writer.write(self._reorder_buffer)
                    await writer.drain()
                    self._reorder_buffer = None

            except asyncio.CancelledError:
                break
            except Exception as ex:
                print(f"[Proxy Error] {ex}")
                break
