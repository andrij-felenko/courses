import asyncio
import time
import struct
import socket
import threading

# Структура телеметрії: 2 uint64, 3 float32, 1 uint32 (32 байти)
TELEMETRY_STRUCT = struct.Struct("<QQfffI")

async def benchmark_in_memory(msg_count: int):
    queue = asyncio.Queue(maxsize=10000)
    
    async def consumer():
        processed = 0
        while processed < msg_count:
            record = await queue.get()
            # Легка бізнес-логіка
            if record[2] > 250.0:
                pass
            processed += 1
            queue.task_done()

    start_time = time.perf_counter()
    consumer_task = asyncio.create_task(consumer())
    
    for i in range(msg_count):
        item = (100000 + (i % 5000), 1724700000000 + i, 230.5, 5.2, 1198.6, 1)
        await queue.put(item)
        
    await consumer_task
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    throughput = msg_count / (elapsed_ms / 1000.0)
    print(f"[Python In-Memory] {msg_count} подій: {elapsed_ms:.2f} мс ({int(throughput)} msg/sec)")

def benchmark_socket(msg_count: int):
    s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    start_time = time.perf_counter()
    
    # Виробник відправляє байти у сокет
    def producer():
        payload = TELEMETRY_STRUCT.pack(100000, 1724700000000, 230.5, 5.2, 1198.6, 1)
        for _ in range(msg_count):
            s1.sendall(payload)
        s1.close()
        
    t = threading.Thread(target=producer)
    t.start()
    
    # Споживач приймає і розпаковує байти
    received = 0
    rec_size = TELEMETRY_STRUCT.size
    while received < msg_count:
        data = s2.recv(rec_size * 100)
        if not data:
            break
        received += len(data) // rec_size
        
    s2.close()
    t.join()
    
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    throughput = msg_count / (elapsed_ms / 1000.0)
    print(f"[Python Socket IPC] {msg_count} подій: {elapsed_ms:.2f} мс ({int(throughput)} msg/sec)")

if __name__ == "__main__":
    COUNT = 100000
    print(f"Старт Python бенчмарку ({COUNT} повідомлень)...")
    asyncio.run(benchmark_in_memory(COUNT))
    benchmark_socket(COUNT)
