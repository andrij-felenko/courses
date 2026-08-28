import re

def handle_command(cmd):
    m = re.fullmatch(r"SPEED (\d+)", cmd)          # "SPEED 120" → value=120

    if cmd == "LED ON":
        digital_write(LED, HIGH)
    elif cmd == "LED OFF":
        digital_write(LED, LOW)
    elif cmd == "STOP":
        set_speed(0)
    elif m:                                         # число зчиталося — відкидає "SPEED abc"
        set_speed(int(m.group(1)))
    else:
        port.write(f"? невідома команда: {cmd}\n".encode())  # відповідь у той самий потік

    port.write(b"OK\n")        # підтвердження — зворотний зв'язок користувачу
