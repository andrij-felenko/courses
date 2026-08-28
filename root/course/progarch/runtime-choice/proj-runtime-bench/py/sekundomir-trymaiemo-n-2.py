# Python + asyncio: одна припаркована задача на кожне сонне з'єднання
import socket, asyncio, sys

def rss_mb():
    for line in open("/proc/self/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return -1.0

async def hold(loop, sock):
    await loop.sock_recv(sock, 1)         # паркується на epoll — ЖОДНОГО потоку

async def main(N):
    loop = asyncio.get_running_loop()
    keep, tasks = [], []
    for _ in range(N):
        a, b = socket.socketpair()
        a.setblocking(False)
        keep.append((a, b))
        tasks.append(asyncio.create_task(hold(loop, a)))
    await asyncio.sleep(0.5)              # дати задачам зареєструватись на циклі
    print(f"{N} задач:   VmRSS≈{rss_mb():.0f} МБ")   # задач НЕ чекаємо — спали б вічно

asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 50000))
# 50 000 задач на одному потоці — і жодної стіни лічильника: тільки RAM під об'єкти.
