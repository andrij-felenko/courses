from collections import deque

pending = deque()   # черга відкладених кадрів

# Спроба передати радіо: важка дія, тож спершу питаємо сторожа.
# Якщо рейка просіла — НЕ передаємо (просадили б її ще глибше, в brownout),
# а відкладаємо кадр до відновлення напруги.
def radio_try_send(frame):
    if not pwr_heavy_ok():          # сторож каже: рейці зараз зле
        pending.append(frame)       # відкласти кадр, не губити
        return False                # передачу поки не робимо
    radio_transmit(frame)           # рейка здорова — б'ємо в ефір
    return True

# Виклик у головному циклі: коли живлення повернулось у OK — дораздати відкладене.
def radio_service():
    while pwr_heavy_ok() and pending:
        frame = pending.popleft()
        radio_transmit(frame)       # напруга дозволяє — випускаємо чергу
