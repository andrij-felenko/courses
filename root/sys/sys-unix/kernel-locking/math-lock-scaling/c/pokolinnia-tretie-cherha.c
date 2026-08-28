struct mcs_node { struct mcs_node *next; int locked; };

static void mcs_lock(struct mcs_node **tail, struct mcs_node *me)
{
    me->next = NULL;
    me->locked = 1;
    struct mcs_node *prev = xchg(tail, me);   /* стати в хвіст: 1 перенесення */
    if (!prev)
        return;                               /* черга була порожня — замок наш */
    WRITE_ONCE(prev->next, me);
    while (READ_ONCE(me->locked))             /* крутимось на СВОЄМУ рядку */
        cpu_relax();
}

static void mcs_unlock(struct mcs_node **tail, struct mcs_node *me)
{
    if (!READ_ONCE(me->next)) {
        if (cmpxchg(tail, me, NULL) == me)
            return;                           /* наступника немає */
        while (!READ_ONCE(me->next))
            cpu_relax();                      /* наступник уже в хвості, ще не дописався */
    }
    WRITE_ONCE(me->next->locked, 0);          /* одне слово в комірку наступника */
}
