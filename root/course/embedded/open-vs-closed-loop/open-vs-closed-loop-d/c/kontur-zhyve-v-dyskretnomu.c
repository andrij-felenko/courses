// викликається таймером рівно раз на dt секунд (напр. 500 Гц → dt = 0.002)
void control_tick(void) {
    float y = read_sensor();          // вибірка: миттєвий вимір виходу
    float e = setpoint - y;           // помилка e = r − y

    float u = controller_step(e);     // обчислення (займає Δ): правило регулятора
                                      // — далі це стане P, потім PI, потім PID

    set_actuator(u);                  // утримання: u діятиме цілий такт dt
}
