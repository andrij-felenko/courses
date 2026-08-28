static int by_waste(const void *a, const void *b)
{
    const struct cache *x = a, *y = b;
    unsigned long wx = x->tail + x->idle, wy = y->tail + y->idle;
    return (wy > wx) - (wy < wx);
}

static int cmd_report(int top)
{
    if (read_slabinfo() < 0) return 1;
    unsigned long all = 0, alltail = 0, allidle = 0;
    for (int i = 0; i < NC; i++) {
        all += C[i].bytes; alltail += C[i].tail; allidle += C[i].idle;
    }
    qsort(C, NC, sizeof C[0], by_waste);

    /* шапку пишемо вручну: printf рахує ширину поля в БАЙТАХ,
       а кирилична літера в UTF-8 займає два — колонки б поїхали */
    puts("кеш                     об'єктів  розмір /слаб   слабів     усього"
         "    хвіст   простій   марно");
    for (int i = 0; i < NC && i < top; i++) {
        const struct cache *c = &C[i];
        printf("%-22s %10lu %7lu %5lu %8lu %10.1f %8.1f %9.1f %6.1f%%\n",
               c->name, c->active_objs, c->objsize, c->objperslab, c->num_slabs,
               mib(c->bytes), mib(c->tail), mib(c->idle),
               c->bytes ? 100.0 * (c->tail + c->idle) / c->bytes : 0.0);
    }
    printf("\nусього в slabinfo: %.0f МіБ, з них хвости %.0f МіБ,"
           " порожні слоти %.0f МіБ (%.1f %% марно)\n",
           mib(all), mib(alltail), mib(allidle),
           all ? 100.0 * (alltail + allidle) / all : 0.0);
    printf("meminfo: Slab %.0f МіБ = SReclaimable %.0f + SUnreclaim %.0f\n",
           meminfo_kb("Slab") / 1024.0, meminfo_kb("SReclaimable") / 1024.0,
           meminfo_kb("SUnreclaim") / 1024.0);
    return 0;
}
