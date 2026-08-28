// НЕПРАВИЛЬНО: sum — локальна, її стирає перша ж пауза
static int pt_average_BAD(pt_t *pt) {
    int sum = 0, i;                    // ← кадр стека
    PT_BEGIN(pt);
    for (i = 0; i < 10; i++) {
        sum += sensor_read();
        PT_WAIT_UNTIL(pt, tick());     // ← тут return: sum та i ГИНУТЬ
    }
    publish(sum / 10);                 // сміття / 10
    PT_END(pt);
}
