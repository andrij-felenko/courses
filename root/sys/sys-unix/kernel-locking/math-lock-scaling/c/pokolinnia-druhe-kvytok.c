struct ticket_lock { u16 next, owner; };

static void ticket_lock(struct ticket_lock *l)
{
    u16 t = xadd(&l->next, 1);          /* атомарно взяти номерок */
    while (READ_ONCE(l->owner) != t)
        cpu_relax();                    /* далі — самі читання */
}

static void ticket_unlock(struct ticket_lock *l)
{
    WRITE_ONCE(l->owner, l->owner + 1); /* викликати наступний номер */
}
