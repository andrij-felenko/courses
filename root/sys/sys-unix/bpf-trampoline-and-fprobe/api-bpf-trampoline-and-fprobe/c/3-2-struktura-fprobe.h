struct fprobe {
    /* Вказівник на масив назв символів або адрес у пам'яті ядра */
    const char **syms;
    size_t nsyms;
    
    /* Колбеки ядра, що викликаються на вході та виході з функції */
    fprobe_entry_cb entry_handler;
    fprobe_exit_cb  exit_handler;
    
    /* Інтеграція з підсистемами ftrace та rethook */
    struct ftrace_ops ops;
    struct rethook   *rethook;
    
    /* Лічильник пропущених подій через вичерпання ресурсів */
    unsigned long nmissed;
};

/* Сигнатури колбеків fprobe у ядрі */
typedef int (*fprobe_entry_cb)(struct fprobe *fp, unsigned long entry_ip,
                               struct pt_regs *regs, void *entry_data);

typedef void (*fprobe_exit_cb)(struct fprobe *fp, unsigned long entry_ip,
                               unsigned long ret_ip, struct pt_regs *regs,
                               void *entry_data);
