#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Tuple
import math

# Тривалість одного символу 802.11ax (12.8 мкс + 0.8 мкс GI) у секундах
T_SYM_SEC = 13.6e-6

# Таблиця кількості піднесучих даних у ресурсних блоках RU
RU_DATA_SUBCARRIERS = {
    26: 24,
    52: 48,
    106: 102,
    242: 234
}

# Співвідношення MCS до кількості біт на піднесучу (з урахуванням FEC rate)
MCS_BITS_PER_SUBCARRIER = {
    0: 0.5,    # BPSK 1/2
    3: 2.5,    # 16-QAM 1/2
    7: 4.5,    # 64-QAM 5/6
    9: 6.667,  # 256-QAM 5/6
    11: 8.333  # 1024-QAM 5/6
}

@dataclass
class ClientRequest:
    client_id: int
    buffer_bytes: int
    mcs: int
    latency_sensitive: bool

@dataclass
class RUAllocation:
    client_id: int
    ru_type: int
    allocated_bytes: int
    frame_duration_us: float

class Wifi6RuScheduler:
    def __init__(self, bandwidth_mhz: int = 20):
        self.bandwidth_mhz = bandwidth_mhz

    def calculate_bits_per_symbol(self, ru_type: int, mcs: int) -> float:
        data_subcarriers = RU_DATA_SUBCARRIERS[ru_type]
        bits_per_sc = MCS_BITS_PER_SUBCARRIER.get(mcs, 1.0)
        return data_subcarriers * bits_per_sc

    def schedule_20mhz(self, clients: List[ClientRequest]) -> Tuple[str, List[RUAllocation]]:
        if not clients:
            return "NO_CLIENTS", []

        # Сортування: спершу критичні до затримки, потім за зростанням буфера
        sorted_clients = sorted(clients, key=lambda c: (not c.latency_sensitive, c.buffer_bytes))
        num_clients = len(sorted_clients)

        # Визначення геометрії RU залежно від кількості клієнтів у черзі
        if num_clients >= 5:
            pattern_name = "9xRU26"
            ru_type = 26
            max_slots = 9
        elif num_clients >= 3:
            pattern_name = "4xRU52"
            ru_type = 52
            max_slots = 4
        elif num_clients == 2:
            pattern_name = "2xRU106"
            ru_type = 106
            max_slots = 2
        else:
            pattern_name = "1xRU242"
            ru_type = 242
            max_slots = 1

        selected_clients = sorted_clients[:max_slots]
        allocations = []

        # Обчислення максимальної тривалості передачі серед обраних клієнтів
        max_symbols = 0
        for client in selected_clients:
            bits_per_sym = self.calculate_bits_per_symbol(ru_type, client.mcs)
            total_bits = client.buffer_bytes * 8
            needed_symbols = math.ceil(total_bits / bits_per_sym) if bits_per_sym > 0 else 1
            max_symbols = max(max_symbols, needed_symbols)

        frame_duration_us = max_symbols * T_SYM_SEC * 1e6

        # Формування результатів розподілу для кожного пристрою
        for client in selected_clients:
            bits_per_sym = self.calculate_bits_per_symbol(ru_type, client.mcs)
            capacity_bytes = math.floor((max_symbols * bits_per_sym) / 8)
            allocated_bytes = min(client.buffer_bytes, capacity_bytes)

            allocations.append(RUAllocation(
                client_id=client.client_id,
                ru_type=ru_type,
                allocated_bytes=allocated_bytes,
                frame_duration_us=frame_duration_us
            ))

        return pattern_name, allocations

def main():
    clients = [
        ClientRequest(client_id=1, buffer_bytes=120, mcs=7,  latency_sensitive=True),  # VoIP
        ClientRequest(client_id=2, buffer_bytes=80,  mcs=9,  latency_sensitive=True),  # Game ACK
        ClientRequest(client_id=3, buffer_bytes=500, mcs=11, latency_sensitive=False), # HTTP
        ClientRequest(client_id=4, buffer_bytes=300, mcs=7,  latency_sensitive=False)  # Sensor
    ]

    scheduler = Wifi6RuScheduler(bandwidth_mhz=20)
    pattern, allocs = scheduler.schedule_20mhz(clients)

    print(f"--- Результат планування Wi-Fi 6 OFDMA (Конфігурація: {pattern}) ---")
    for a in allocs:
        print(f"Клієнт #{a.client_id}: RU{a.ru_type} | Передано: {a.allocated_bytes} байт | Тривалість кадру: {a.frame_duration_us:.2f} мкс")

if __name__ == "__main__":
    main()
