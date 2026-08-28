# Python + потоки: один потік на кожне сонне з'єднання
import socket, threading, sys, time

def stat_mb(field):                       # поле з /proc/self/status, КБ → МБ
    for line in open("/proc/self/status"):
        if line.startswith(field):
            return int(line.split()[1]) / 1024
    return -1.0

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
keep = []                                 # тримаємо обидва кінці, щоб не закрились

def hold(sock):
    sock.recv(1)                          # блокує НАЗАВЖДИ — з'єднання «спить»

for _ in range(N):
    a, b = socket.socketpair()
    keep.append((a, b))
    threading.Thread(target=hold, args=(a,), daemon=True).start()

time.sleep(0.5)                           # дати потокам осісти на recv
print(f"{N} потоків:  VmRSS≈{stat_mb('VmRSS:'):6.0f} МБ   "
      f"VmSize≈{stat_mb('VmSize:'):8.0f} МБ")
# Спробуй N=2000, тоді N=20000 — і побач, як VmSize росте на 8 МБ/потік,
# а десь коло десятків тисяч потік просто перестане створюватись: стіна.
