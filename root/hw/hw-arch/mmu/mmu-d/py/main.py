# Спрощена модель того, що MMU робить у залізі щодоступу.
PAGE_BITS = 12                 # сторінка 4 КБ = 2^12
PAGE_SIZE = 1 << PAGE_BITS
OFFS_MASK = PAGE_SIZE - 1      # молодші 12 бітів

def translate(page_table, virt):
    page   = virt >> PAGE_BITS       # старші біти — номер сторінки
    offset = virt & OFFS_MASK        # молодші — зсув
    frame  = page_table[page]        # де ця сторінка фізично
    return (frame << PAGE_BITS) | offset   # склеїти кадр і зсув
