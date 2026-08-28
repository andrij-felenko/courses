import asyncio
import time

class VirtualDeviceNode:
    def __init__(self, node_id: int, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.seq_num = 0
        self.tx_count = 0
        self.rx_count = 0
        self.errors = 0

    async def run(self):
        # Рандомізований старт для уникнення Thundering Herd
        await asyncio.sleep(random.uniform(0.1, 5.0))

        while True:
            try:
                reader, writer = await asyncio.open_connection(self.host, self.port)
                
                while True:
                    self.seq_num += 1
                    # Формуємо телеметричний бінарний кадр
                    payload = struct.pack("<HII", self.node_id, self.seq_num, int(time.time()))
                    frame = build_cobs_frame(msg_type=0x02, payload=payload)

                    t_start = time.monotonic()
                    writer.write(frame)
                    await writer.drain()
                    self.tx_count += 1

                    # Очікуємо підтвердження ACK
                    response = await asyncio.wait_for(reader.read(128), timeout=2.0)
                    rtt_ms = (time.monotonic() - t_start) * 1000.0
                    
                    if verify_ack(response, self.seq_num):
                        self.rx_count += 1
                    else:
                        self.errors += 1

                    # Пауза між вимірюваннями з експоненційним джитером
                    await asyncio.sleep(random.uniform(0.8, 1.2))

            except (asyncio.TimeoutError, ConnectionResetError, OSError):
                self.errors += 1
                # Експоненційний відступ при збої з джитером
                await asyncio.sleep(random.uniform(1.0, 3.0))

async def run_scale_test(total_nodes: int = 500):
    print(f"[*] Запуск навантажувального тесту з {total_nodes} віртуальними вузлами...")
    nodes = [VirtualDeviceNode(i, "127.0.0.1", 8080) for i in range(total_nodes)]
    await asyncio.gather(*(n.run() for n in nodes))
