struct kprobe {
    /* Хеш-вузол внутрішньої таблиці зондів ядра */
    struct hlist_node hlist;

    /* Список зондів, якщо на одну адресу встановлено кілька зондів */
    struct list_node list;

    /* Оптимізований зонд (якщо використовується Optprobe) */
    struct kprobe_optins optins;

    /* Назва символу в ядрі (наприклад, "do_sys_openat2") */
    const char *symbol_name;

    /* Точна віртуальна адреса зонду (якщо symbol_name == NULL) */
    kprobe_opcode_t *addr;

    /* Зміщення від початку символу в байтах */
    unsigned int offset;

    /* Обробник, що викликається БЕРЕД виконанням оригінальної інструкції */
    kprobe_pre_handler_t pre_handler;

    /* Обробник, що викликається ПІСЛЯ виконання оригінальної інструкції */
    kprobe_post_handler_t post_handler;

    /* Обробник помилок адресації або сторінкових збоїв (faults) */
    kprobe_fault_handler_t fault_handler;

    /* Збережений оригінальний машинний код інструкції */
    kprobe_opcode_t opcode;

    /* Буфер для Out-Of-Line (OOL) виконання інструкції */
    struct arch_specific_insn ainsn;

    /* Прапорці стану зонду (KPROBE_FLAG_DISABLED тощо) */
    u32 flags;
};
