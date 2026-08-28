#define __DO_TRACE(tp, proto, args, cond, rcuidle)                     \
    do {                                                               \
        struct tracepoint_func *it_func_ptr;                           \
        void *it_func;                                                 \
        void *__data;                                                  \
                                                                       \
        if (!(cond))                                                   \
            return;                                                    \
                                                                       \
        /* Вхід у критичну секцію RCU-читача */                        \
        rcu_read_lock_sched();                                         \
        it_func_ptr = rcu_dereference_raw((tp)->funcs);                \
                                                                       \
        if (it_func_ptr) {                                             \
            do {                                                       \
                it_func = (it_func_ptr)->func;                         \
                __data = (it_func_ptr)->data;                          \
                ((void(*)(proto))(it_func))(__data, args);             \
            } while ((++it_func_ptr)->func);                           \
        }                                                              \
        rcu_read_unlock_sched();                                       \
    } while (0)
