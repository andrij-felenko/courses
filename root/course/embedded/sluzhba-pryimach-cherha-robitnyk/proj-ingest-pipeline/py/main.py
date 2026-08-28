import asyncio
import struct
import time
from dataclasses import dataclass
from typing import Optional, List

# 1. Специфікація кадру та розпакування
CRC16_POLY = 0x1021

def calculate_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ CRC16_POLY) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

@dataclass
class RawPacket:
    payload: bytes
    ingress_time: float
    peer_id: int

@dataclass
class NormalizedEvent:
    device_id: str
    timestamp_utc: float
    temperature_c: float
    humidity_pct: float
    battery_v: float
    seq_num: int
    is_valid: bool

def parse_telemetry_frame(packet: RawPacket) -> Optional[NormalizedEvent]:
    if len(packet.payload) != 24:
        return None
    
    # 24 байти розкладки
    magic, ver, flags = struct.unpack(">HBB", packet.payload[0:4])
    if magic != 0xAA55 or ver != 0x01:
        return None
    
    # Перевірка CRC16
    expected_crc, = struct.unpack(">H", packet.payload[22:24])
    actual_crc = calculate_crc16(packet.payload[0:22])
    if expected_crc != actual_crc:
        return None
    
    dev_id, uptime_ms, raw_temp, raw_hum, raw_vbat, seq, status = struct.unpack(
        ">IIhhHHH", packet.payload[4:22]
    )
    
    temp_c = raw_temp * 0.01
    hum_pct = raw_hum * 0.01
    vbat_v = raw_vbat * 0.001
    
    is_valid = (-40.0 <= temp_c <= 125.0) and (0.0 <= hum_pct <= 100.0)
    
    return NormalizedEvent(
        device_id=f"esp32-{dev_id:08x}",
        timestamp_utc=packet.ingress_time,
        temperature_c=round(temp_c, 2),
        humidity_pct=round(hum_pct, 2),
        battery_v=round(vbat_v, 3),
        seq_num=seq,
        is_valid=is_valid
    )

# 2. Демпферна черга з контролем ватерпостів
class BoundedIngestQueue:
    def __init__(self, capacity: int, high_ratio: float = 0.85, low_ratio: float = 0.60):
        self.capacity = capacity
        self.high_watermark = int(capacity * high_ratio)
        self.low_watermark = int(capacity * low_ratio)
        self._queue: List[RawPacket] = []
        self._cv = asyncio.Condition()
        self.backpressure_active = False
        self.dropped_count = 0
        self.is_stopped = False

    async def push(self, packet: RawPacket):
        async with self._cv:
            if len(self._queue) >= self.capacity:
                self._queue.pop(0)  # Drop Oldest
                self.dropped_count += 1
            
            self._queue.append(packet)
            
            if len(self._queue) >= self.high_watermark:
                self.backpressure_active = True
            
            self._cv.notify()

    async def pop(self) -> Optional[RawPacket]:
        async with self._cv:
            while not self._queue and not self.is_stopped:
                await self._cv.wait()
            
            if self.is_stopped and not self._queue:
                return None
            
            packet = self._queue.pop(0)
            
            if len(self._queue) <= self.low_watermark:
                self.backpressure_active = False
                
            return packet

    async def stop(self):
        async with self._cv:
            self.is_stopped = True
            self._cv.notify_all()

# 3. Конвеєр та тест пікового навантаження
async def telemetry_worker(worker_id: int, queue: BoundedIngestQueue, results: list):
    while True:
        packet = await queue.pop()
        if packet is None:
            break
        event = parse_telemetry_frame(packet)
        if event and event.is_valid:
            results.append(event)

def make_mock_frame(dev_id: int, seq: int) -> bytes:
    header = struct.pack(">HBB", 0xAA55, 1, 0)
    body = struct.pack(">IIhhHHH", dev_id, seq * 100, 2345, 5820, 3820, seq, 0x07)
    crc = calculate_crc16(header + body)
    return header + body + struct.pack(">H", crc)

async def main():
    print("Starting Python Telemetry Ingestion Pipeline (asyncio)...")
    queue = BoundedIngestQueue(capacity=1000, high_ratio=0.80, low_ratio=0.50)
    results = []
    
    # 4 воркери
    workers = [asyncio.create_task(telemetry_worker(i, queue, results)) for i in range(4)]
    
    # Генерація пікового залпу
    start_time = time.perf_counter()
    TOTAL_BURST = 5000
    
    for seq in range(TOTAL_BURST):
        frame = make_mock_frame(0x000104A2, seq)
        await queue.push(RawPacket(payload=frame, ingress_time=time.time(), peer_id=seq % 50))
    
    await queue.stop()
    await asyncio.gather(*workers)
    
    elapsed = time.perf_counter() - start_time
    print("--- Ingestion Summary ---")
    print(f"Total Sent:     {TOTAL_BURST}")
    print(f"Processed Valid:{len(results)}")
    print(f"Dropped:        {queue.dropped_count}")
    print(f"Elapsed:        {elapsed:.3f} s")
    print(f"Throughput:     {TOTAL_BURST / elapsed:.1f} frames/s")

if __name__ == "__main__":
    asyncio.run(main())
