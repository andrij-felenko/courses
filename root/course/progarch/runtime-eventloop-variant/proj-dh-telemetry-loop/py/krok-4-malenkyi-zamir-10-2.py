# ПОТІК НА З'ЄДНАННЯ: одне з'єднання = один OS-потік, заблокований на recv.
import socket, threading

def hold(conn):
    conn.recv(1)                               # блокується — увесь стек СТОЇТЬ

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 9101)); srv.listen(10_000)
while True:
    conn, _ = srv.accept()
    threading.Thread(target=hold, args=(conn,), daemon=True).start()
# 10 000 потоків × 8 МБ стек = 80 ГБ віртуальних — система відмовить,
# доки стек не вріжеш; навіть врізаний — RSS на сотні МБ + тасування 10⁴ потоків
