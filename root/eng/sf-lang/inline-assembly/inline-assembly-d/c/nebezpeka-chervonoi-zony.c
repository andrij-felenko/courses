/* КАТАСТРОФА: push знищує змінні у Red Zone */
void broken_stack_usage(int val) {
    int local_data = val * 10; /* Компілятор може тримати local_data у Red Zone: -8(%rsp) */
    __asm__ __volatile__ (
        "pushq %0\n\t"         /* Записує значення за адресою -8(%rsp), затираючи local_data! */
        "popq %%rax"
        :
        : "r" ((uint64_t)val)
        : "rax"
    );
    /* local_data тепер містить сміття */
}
