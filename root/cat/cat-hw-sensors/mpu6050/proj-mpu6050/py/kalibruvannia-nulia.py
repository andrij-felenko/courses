def calibrate_gyro():
    global gyro_bias_x, gyro_bias_y
    N = 2000                          # скільки зразків усереднити
    sum_x = sum_y = sum_z = 0

    print("Калібрую гіроскоп — НЕ РУХАЙ плату 5 секунд...")
    sleep_ms(1000)                    # дати руці прибратись, платі — заспокоїтись

    for _ in range(N):
        _, _, _, gx, gy, gz = read6()
        sum_x += gx;  sum_y += gy;  sum_z += gz
        sleep_ms(2)                   # ~2 мс між зразками

    gyro_bias_x = sum_x / N           # середнє = сталий зсув нуля
    gyro_bias_y = sum_y / N
    # gyro_bias_z = sum_z / N         # за потреби

    print("Зсув нуля гіроскопа:", gyro_bias_x, gyro_bias_y)
