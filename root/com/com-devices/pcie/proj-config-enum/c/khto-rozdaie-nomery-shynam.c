static uint8_t next_bus;                     /* лічильник виданих номерів; на старті 0 */

static void assign_bus(uint8_t bus, uint8_t dev, uint8_t fn)
{
    uint8_t sec = ++next_bus;

    cfg_w8(bus, dev, fn, 0x18, bus);         /* первинна  — де стоїть сам міст */
    cfg_w8(bus, dev, fn, 0x19, sec);         /* підлегла  — перша шина за мостом */
    cfg_w8(bus, dev, fn, 0x1A, 0xFF);        /* гранична  — поки що «пропускай геть усе» */

    scan_bus_assign(sec);                    /* спуск у глибину: усі номери під нами > sec */

    cfg_w8(bus, dev, fn, 0x1A, next_bus);    /* тепер справжній максимум піддерева відомий */
}
