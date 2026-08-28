# Три ноги Голлів у молодших бітах: (HC<<2)|(HB<<1)|HA -> код 1..6.
# Значення 0 і 7 — несправність (обрив/КЗ датчика або шум).
# sector_of_hall[код] = номер сектора 0..5, або None як "недійсно".
SECTOR_OF_HALL = [
    None,  # 000 — недійсно
    0,     # 001 -> сектор 1
    2,     # 010 -> сектор 3
    1,     # 011 -> сектор 2
    4,     # 100 -> сектор 5
    5,     # 101 -> сектор 6
    3,     # 110 -> сектор 4
    None,  # 111 — недійсно
]

def read_hall_code():
    # Прочитати три ноги портів; тут — умовні функції читання піна.
    a = gpio_read(HALL_A_PIN)
    b = gpio_read(HALL_B_PIN)
    c = gpio_read(HALL_C_PIN)
    return (c << 2) | (b << 1) | a

def commutate_from_hall(forward):
    code = read_hall_code()
    sector = SECTOR_OF_HALL[code]
    if sector is None:
        drive_off()             # недійсний код -> знеструмити міст, не гадати
        fault_latch(FAULT_HALL)
        return
    bits = step_bits(sector, forward)
    apply_inverter(bits)        # виставити ключі на цей сектор
