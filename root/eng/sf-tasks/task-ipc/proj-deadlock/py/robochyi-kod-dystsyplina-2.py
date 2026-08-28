# ✓ БЕЗПЕЧНО: ЄДИНИЙ порядок для ВСІХ — завжди spi_mtx ПЕРЕД sd_mtx
#   (домовленість, що рве умову №4 «кругове очікування»)
def take_both():                   # спільний хелпер — один порядок на весь код
    spi_mtx.acquire()              # 1) завжди spi
    sd_mtx.acquire()               # 2) потім sd

def give_both():                   # віддаємо у ЗВОРОТНОМУ порядку
    sd_mtx.release()
    spi_mtx.release()

# тепер і task_a, і task_b викликають take_both()/give_both() — кільце неможливе
