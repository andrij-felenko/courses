import threading, time

spi_mtx = threading.Lock()         # два спільні ресурси, кожен під своїм м'ютексом
sd_mtx  = threading.Lock()

# ✗ НЕБЕЗПЕЧНО: потоки беруть замки в РІЗНОМУ порядку → можливий дедлок
def task_a():                      # A: spi, потім sd
    while True:
        spi_mtx.acquire()
        sd_mtx.acquire()           # ← чекає на sd, тримаючи spi
        draw_and_log()
        sd_mtx.release()
        spi_mtx.release()
        time.sleep(0.02)

def task_b():                      # B: sd, потім spi  ← ПРОТИЛЕЖНИЙ порядок!
    while True:
        sd_mtx.acquire()
        spi_mtx.acquire()          # ← кільце замикається тут
        log_and_draw()
        spi_mtx.release()
        sd_mtx.release()
        time.sleep(0.02)
