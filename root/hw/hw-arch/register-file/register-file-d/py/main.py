regfile = [0] * 32                    # 32 регістри по 32 біти
MASK32 = 0xFFFFFFFF

# два порти читання — комбінаційні: просто дивимось у масив
def rf_read(addr):
    return regfile[addr & 31]         # 5-бітна адреса

# порт запису — «спрацьовує» на фронті такту (виклик = фронт)
def rf_write_on_edge(addr, data, wen):
    if wen:
        regfile[addr & 31] = data & MASK32
