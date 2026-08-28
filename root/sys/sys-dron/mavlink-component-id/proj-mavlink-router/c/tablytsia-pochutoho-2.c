static void route_learn(uint8_t sysid, uint8_t compid, uint8_t chan, uint32_t now)
{
    if (sysid == 0 || compid == 0)      /* нуль не буває адресою відправника */
        return;

    uint8_t  victim = 0;
    uint32_t oldest = 0;

    for (uint8_t i = 0; i < route_n; i++) {
        route_t *r = &routes[i];
        if (r->sysid == sysid && r->compid == compid && r->chan == chan) {
            r->seen_ms = now;           /* знайомий вузол на знайомому каналі */
            return;
        }
        uint32_t age = now - r->seen_ms;
        if (age >= oldest) { oldest = age; victim = i; }
    }

    if (route_n < ROUTE_MAX)                         /* є вільне місце        */
        routes[route_n++] = (route_t){ sysid, compid, chan, now };
    else if (oldest > ROUTE_TTL_MS)                  /* витісняємо лиш протухле */
        routes[victim]   = (route_t){ sysid, compid, chan, now };
    /* інакше таблиця повна живими вузлами — новачка не запам'ятовуємо */
}
