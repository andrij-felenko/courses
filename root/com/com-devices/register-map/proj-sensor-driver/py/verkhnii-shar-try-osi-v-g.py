def main():
    if not mpu_present():
        return                      # біда з дротами/адресою
    mpu_begin()                     # збій налаштування підніме OSError

    while True:
        try:
            ax, ay, az = mpu_read_accel()
        except OSError:
            continue                # обмін не вдався — пропускаємо цей цикл
        # ax, ay, az — у g, можна використовувати

main()
