// було (v1.4.0): таймер гладимо тільки в кінці циклу —
// у важкому режимі цикл затягувався й сторож скидав чіп
void main_loop(void) {
    while (1) {
        do_sensors();
        do_heavy_mode();   // інколи > періоду сторожа → reset
        watchdog_kick();   // не встигало
    }
}

// стало (v1.4.1, гілка hotfix): гладимо ще й усередині важкого кроку
void main_loop(void) {
    while (1) {
        do_sensors();
        watchdog_kick();   // гарантований дотик до сторожа
        do_heavy_mode();
        watchdog_kick();
    }
}
