/* RCU — linux/rcupdate.h */
rcu_read_lock();                    /* законний будь-де, зокрема в NMI */
p = rcu_dereference(gp);            /* читати вказівник тільки так */
/* ... користуємося p; спати тут НЕ можна ... */
rcu_read_unlock();

rcu_assign_pointer(gp, new);        /* письменник підміняє вказівник */
synchronize_rcu();                  /* СПИТЬ: лише контекст задачі */
call_rcu(&old->rcu, free_cb);       /* відкладене звільнення; можна з атомарного контексту */
kfree_rcu(old, rcu);                /* те саме для простого kfree */

int idx = srcu_read_lock(&ss);      /* різновид, у ділянці якого спати МОЖНА */
srcu_read_unlock(&ss, idx);         /* повернути рівно той індекс, що дали */
