/* верхня половина: біжить із вимкненими перериваннями */
static irqreturn_t sensor_hardirq(int irq, void *dev_id)
{
    struct sensor *s = dev_id;

    /* Спитати «чи наше це переривання» нема в кого: регістр стану лежить
       за шиною. Тому лінія цього давача мусить бути лише його.        */
    s->stamp = ktime_get_ns();
    return IRQ_WAKE_THREAD;       /* усе інше вимагає шини, тобто сну */
}

/* нижня половина: окрема задача, тут спати можна */
static irqreturn_t sensor_thread(int irq, void *dev_id)
{
    struct sensor *s = dev_id;
    u8 buf[6];

    i2c_master_recv(s->client, buf, sizeof(buf));  /* сон на шині — дозволено */
    push_sample(s, buf, s->stamp);
    wake_up_interruptible(&s->readers);
    return IRQ_HANDLED;
}

    err = request_threaded_irq(client->irq, sensor_hardirq, sensor_thread,
                               IRQF_ONESHOT, "sensor", s);
