#!/usr/bin/env python3
"""Агент послідовного пристрою: живе рівно стільки, скільки живе пристрій."""
import errno, os, select, signal, sys, termios

SPEED = termios.B115200


def open_port(path):
    # O_NOCTTY — не робити цей термінал керівним для процесу.
    # O_NONBLOCK — не зависнути в open, чекаючи на сигнал носія.
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    iflag, oflag, cflag, lflag, _, _, cc = termios.tcgetattr(fd)
    iflag = 0                        # без перекладів CR/LF і без XON/XOFF
    oflag = 0
    lflag = 0                        # сирий режим: без рядків і без відлуння
    cflag = termios.CS8 | termios.CREAD | termios.CLOCAL
    cc = list(cc)
    cc[termios.VMIN] = 1
    cc[termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW,
                      [iflag, oflag, cflag, lflag, SPEED, SPEED, cc])
    termios.tcflush(fd, termios.TCIFLUSH)
    return fd


def main(path):
    # Самопіпа: обробник сигналу лише будить select, рішення ухвалює цикл.
    wake_r, wake_w = os.pipe()
    os.set_blocking(wake_w, False)
    signal.set_wakeup_fd(wake_w)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: None)   # без обробника fd не збудять

    fd, tail = open_port(path), b""
    print(f"агент {path}: почали", flush=True)

    while True:
        ready, _, _ = select.select([fd, wake_r], [], [])
        if wake_r in ready:
            print("SIGTERM: закриваємо порт", flush=True)
            break
        try:
            chunk = os.read(fd, 4096)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                continue
            if e.errno in (errno.EIO, errno.ENXIO, errno.ENODEV):
                print("пристрій зник", flush=True)
                break                         # НЕ помилка, інакше перезапустять
            raise
        if not chunk:                         # POLLHUP: шнур висмикнули
            print("порт закрито з того боку", flush=True)
            break
        tail += chunk
        *lines, tail = tail.split(b"\n")
        for ln in lines:
            print("верстат:", ln.rstrip(b"\r").decode("ascii", "replace"),
                  flush=True)                 # stdout забирає journald

    os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
