import time
from pymavlink import mavutil

# Прочитати з лінка все, що накопичилось, і якщо серед розібраного є
# COMMAND_ACK саме на очікувану команду — віддати його. Не блокує:
# щойно черга порожня, recv_match повертає None і ми виходимо з None.
def poll_command_ack(m, want_cmd):
    while True:
        msg = m.recv_match(type='COMMAND_ACK', blocking=False)
        if msg is None:
            return None                 # на лінії наразі потрібного ACK немає
        if msg.command == want_cmd:     # звіряємо command — чужі ACK ігноруємо
            return msg
        # тут-таки крутимо приймання решти телеметрії, щоб не «оглухнути»


# Зібрати й відіслати один кадр COMMAND_LONG.
def send_command(m, cmd, confirmation, p1, p2, p3, p4, p5, p6, p7):
    m.mav.command_long_send(
        m.target_system, m.target_component,
        cmd, confirmation,
        p1, p2, p3, p4, p5, p6, p7)


# Надіслати команду й дочекатися результату.
# Повертає код MAV_RESULT, або None, якщо ACK так і не прийшов за всі спроби.
def send_command_blocking(m, cmd, p1, p2=0, p3=0, p4=0, p5=0, p6=0, p7=0,
                          ack_timeout_s=1.0, max_tries=4):
    for attempt in range(max_tries):
        send_command(m, cmd, attempt, p1, p2, p3, p4, p5, p6, p7)  # confirmation = № спроби
        deadline = time.time() + ack_timeout_s
        while time.time() < deadline:
            ack = poll_command_ack(m, cmd)
            if ack is not None:
                if ack.result == mavutil.mavlink.MAV_RESULT_IN_PROGRESS:
                    deadline = time.time() + 5.0   # довга дія: відсунути таймаут, чекати далі
                    continue
                return ack.result                  # ACCEPTED / DENIED / FAILED / UNSUPPORTED…
            # тут-таки крутимо приймання телеметрії, щоб не «оглухнути» на час очікування
        # таймаут вийшов — наступна ітерація перешле ту саму команду з confirmation+1
    return None   # апарат мовчить: лінк мертвий або апарат не відповідає


# Виклик: озброїти апарат.
r = send_command_blocking(m, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1.0)  # param1=1
if r == mavutil.mavlink.MAV_RESULT_ACCEPTED:
    pass    # мотори озброєно
elif r == mavutil.mavlink.MAV_RESULT_DENIED:
    pass    # не пройшли передпольотні перевірки
elif r is None:
    pass    # зв'язку немає — у безпечний стан
