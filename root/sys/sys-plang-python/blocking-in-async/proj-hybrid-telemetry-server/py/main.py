import asyncio
import hashlib
import os
import signal
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# --- 1. Синхронні функції-виконавці ---

def compute_heavy_hash(data: bytes, iterations: int = 150_000) -> str:
    """CPU-bound задача: виконується у ProcessPoolExecutor (окремий процес, власний GIL)."""
    salt = b"telemetry_salt_2026"
    derived = hashlib.pbkdf2_hmac("sha512", data, salt, iterations)
    return derived.hex()

def sync_append_log(filepath: str, record: str) -> int:
    """I/O-bound задача: виконується у ThreadPoolExecutor (системний потік, спільна купа)."""
    with open(filepath, "a", encoding="utf-8") as f:
        bytes_written = f.write(record + "\n")
        f.flush()
        os.fsync(f.fileno())  # Гарантований запис на фізичний носій
    return bytes_written

# --- 2. Асинхронний диспетчер ---

class HybridTelemetryServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 9090, max_concurrency: int = 50):
        self.host = host
        self.port = port
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.log_file = "telemetry_records.log"
        self.is_running = True
        
        # Ініціалізація виділених пулів
        cpu_cores = os.cpu_count() or 2
        self.process_pool = ProcessPoolExecutor(max_workers=cpu_cores)
        self.io_pool = ThreadPoolExecutor(max_workers=16, thread_name_prefix="DiskIOWorker")

    async def process_payload(self, raw_data: bytes) -> str:
        """Повний конвеєр обробки з ізоляцією блокувальних етапів."""
        async with self.semaphore:
            loop = asyncio.get_running_loop()
            
            # Етап 1: Делегування CPU-bound обчислень у пул процесів
            signature = await loop.run_in_executor(
                self.process_pool,
                compute_heavy_hash,
                raw_data,
                100_000
            )
            
            # Етап 2: Формування запису
            timestamp = time.time()
            log_entry = f"{timestamp:.4f} | {signature[:16]} | {len(raw_data)} bytes"
            
            # Етап 3: Делегування дискового запису у пул потоків
            await loop.run_in_executor(
                self.io_pool,
                sync_append_log,
                self.log_file,
                log_entry
            )
            
            return signature

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Обробник клієнтського TCP-з'єднання."""
        client_addr = writer.get_extra_info("peername")
        try:
            while self.is_running:
                data = await reader.read(4096)
                if not data:
                    break  # Клієнт закрив з'єднання
                
                # Обробка даних через гібридний конвеєр
                sig = await self.process_payload(data)
                
                response = f"OK {sig[:32]}\n".encode("utf-8")
                writer.write(response)
                await writer.drain()
        except asyncio.CancelledError:
            pass
        except Exception as err:
            print(f"Помилка клієнта {client_addr}: {err}", file=sys.stderr)
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self):
        """Запуск сервера та обробка сигналів завершення."""
        loop = asyncio.get_running_loop()
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"[*] Гібридний сервер запущено на {addr[0]}:{addr[1]}")

        # Реєстрація граціозного завершення
        stop_event = asyncio.Event()

        def signal_handler():
            print("\n[!] Отримано сигнал зупинки. Завершення роботи...")
            self.is_running = False
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, signal_handler)
            except NotImplementedError:
                # Windows не підтримує add_signal_handler для всіх сигналів
                pass

        async with server:
            await stop_event.wait()
            print("[*] Зупинка TCP-сервера...")
            server.close()
            await server.wait_closed()

        print("[*] Закриття пулів виконання...")
        # Зупинка пулів: потоки завершують дисковий I/O, процеси завершують розрахунки
        self.process_pool.shutdown(wait=True, cancel_futures=True)
        self.io_pool.shutdown(wait=True, cancel_futures=True)
        print("[*] Всі ресурси успішно звільнено.")

if __name__ == "__main__":
    try:
        asyncio.run(HybridTelemetryServer().run())
    except KeyboardInterrupt:
        pass
