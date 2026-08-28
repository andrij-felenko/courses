/* Канали, де чули названу ціль. tcomp = 0 — будь-який вузол системи tsys. */
static uint8_t target_mask(uint8_t tsys, uint8_t tcomp, uint32_t now)
{
    if (tsys == 0)                              /* оголошення — потенційно всім */
        return (uint8_t)((1u << NCHAN) - 1u);

    uint8_t mask = 0;
    for (uint8_t i = 0; i < route_n; i++) {
        const route_t *r = &routes[i];
        if (!fresh(r, now))              continue;
        if (r->sysid != tsys)            continue;
        if (tcomp && r->compid != tcomp) continue;
        mask |= (uint8_t)(1u << r->chan);
    }
    return mask;                                /* 0 — пари не чули ніде: мовчимо */
}

/* Канали, на яких ми вже чули самого відправника цього пакета. */
static uint8_t source_mask(uint8_t sysid, uint8_t compid, uint32_t now)
{
    uint8_t mask = 0;
    for (uint8_t i = 0; i < route_n; i++) {
        const route_t *r = &routes[i];
        if (fresh(r, now) && r->sysid == sysid && r->compid == compid)
            mask |= (uint8_t)(1u << r->chan);
    }
    return mask;
}
