// «мозок»: викликати повільно, 1..10 Гц. Це НЕ гарячий шлях.
void balancer_tick(balancer_t *b)
{
    if (!window_open()) {                 // вийшли з вікна — негайно стоп
        shuttle_stop();
        b->state = BAL_IDLE;
        return;
    }

    uint16_t v[NCELLS];
    cellmon_read(v);                      // сам паузить шатл на час виміру (див. пастки)

    uint8_t hi, lo;
    find_extremes(v, &hi, &lo);
    uint16_t spread = (uint16_t)(v[hi] - v[lo]);

    switch (b->state) {
    case BAL_IDLE:
        if (spread > VSTART_MV) {         // розкид переріс поріг пуску
            b->donor = hi; b->recipient = lo;
            b->state = BAL_ACTIVE;
            shuttle_start(hi, lo);
        }
        break;

    case BAL_ACTIVE:
        if (spread < VSTOP_MV) {          // зійшлися — гістерезисний стоп
            shuttle_stop();
            b->state = BAL_IDLE;
        } else if (hi != b->donor || lo != b->recipient) {
            shuttle_stop();               // пара змінилась: спершу РОЗІМКНУТИ,
            b->donor = hi; b->recipient = lo;
            shuttle_start(hi, lo);        // аж тоді нова пара
        }
        break;
    }
}
