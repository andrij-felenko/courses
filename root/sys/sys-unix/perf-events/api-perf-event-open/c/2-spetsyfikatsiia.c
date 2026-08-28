/* Структура конфігурації perf_event у C UAPI header <linux/perf_event.h> */
struct perf_event_attr {
    __u32 type;                 /* Тип події (PERF_TYPE_*) */
    __u32 size;                 /* Розмір структури sizeof(struct perf_event_attr) */
    __u64 config;               /* Конфігурація конкретної події */

    union {
        __u64 sample_period;    /* Період вибірки (кількість подій на NMI) */
        __u64 sample_freq;      /* Динамічна частота вибірки у Гц */
    };

    __u64 sample_type;          /* Бітова маска полів, що записуються у вибірку */
    __u64 read_format;          /* Формат даних при виклику read() */

    __u64 disabled       : 1,   /* Подія створюється у вимкненому стані */
          inherit        : 1,   /* Успадковувати подію дочірніми потоками (fork) */
          pinned         : 1,   /* Подія має залишатися на HW PMC (лише для лідерів) */
          exclusive      : 1,   /* Захоплює HW PMC монопольно */
          exclude_user   : 1,   /* Не рахувати події у user-space (ring 3) */
          exclude_kernel : 1,   /* Не рахувати події у kernel-space (ring 0) */
          exclude_hv     : 1,   /* Не рахувати події у гіпервізорі (KVM/Xen) */
          exclude_idle   : 1,   /* Не рахувати події коли CPU перебуває в idle */
          mmap           : 1,   /* Відстежувати виклики mmap (PERF_RECORD_MMAP) */
          comm           : 1,   /* Відстежувати зміни імені процесу (PERF_RECORD_COMM) */
          freq           : 1,   /* Використовувати sample_freq замість sample_period */
          inherit_stat   : 1,   /* Збирати статистику для дочірніх процесів */
          enable_on_exec : 1,   /* Автоматично вмикати подію при execve() */
          task           : 1,   /* Генерувати події fork/exit (PERF_RECORD_FORK/EXIT) */
          watermark      : 1,   /* Сигналізувати wakeup_watermark байтів у буфері */
          precise_ip     : 2,   /* Рівень точності RIP (0..3, PEBS/IBS) */
          mmap_data      : 1,   /* Відстежувати mmap для даних (non-executable) */
          sample_id_all  : 1,   /* Додавати TID/TIME до усіх типів PERF_RECORD_* */
          exclude_host   : 1,   /* Не рахувати події хоста у віртуалізації */
          exclude_guest  : 1,   /* Не рахувати події гостя у віртуалізації */
          exclude_callchain_kernel : 1, /* Виключити стек ядра з callchain */
          exclude_callchain_user   : 1, /* Виключити стек користувача з callchain */
          mmap2          : 1,   /* Розширені події mmap (PERF_RECORD_MMAP2) */
          comm_exec      : 1,   /* Помічати зміни COMM зумовлені саме execve() */
          use_clockid    : 1,   /* Використовувати специфічний clockid */
          context_switch : 1,   /* Записувати перемикання контексту */
          write_backward : 1,   /* Кільцевий буфер записується у зворотному напрямку */
          namespaces     : 1,   /* Записувати події зміни namespaces */
          ksymbol        : 1,   /* Записувати події завантаження kallsyms */
          bpf_event      : 1,   /* Записувати події завантаження/видалення BPF-програм */
          aux_output     : 1,   /* Перенаправляти вихід у AUX-буфер (Intel PT) */
          cgroup         : 1,   /* Записувати ідентифікатори cgroup */
          text_poke      : 1,   /* Записувати зміни коду ядра (kprobes/ftrace) */
          build_id       : 1,   /* Додавати Build-ID до подій MMAP2 */
          inherit_thread : 1,   /* Успадковувати лише потоками (не новими процесами) */
          remove_on_exec : 1,   /* Видаляти подію при виконанні execve() */
          sigtrap        : 1,   /* Надсилати SIGTRAP при переповненні замість NMI */
          __reserved_1   : 26;

    union {
        __u32 wakeup_events;    /* Кількість вибірок до генерування POLL_IN */
        __u32 wakeup_watermark; /* Кількість байтів у буфері до POLL_IN */
    };

    __u32 bp_type;              /* Тип HW Точки зупинки (HW_BREAKPOINT_R/W/X) */

    union {
        __u64 bp_addr;          /* Віртуальна адреса точки зупинки */
        __u64 kprobe_func;      /* Адреса або ім'я функції для kprobe */
        __u64 uprobe_path;      /* Шлях до ELF-файлу для uprobe */
        __u64 config1;          /* Додаткові параметри розширеного PMU */
    };

    union {
        __u64 bp_len;           /* Довжина маски точки зупинки (1, 2, 4, 8 байтів) */
        __u64 kprobe_addr;      /* Зсув всередині функції kprobe */
        __u64 probe_offset;     /* Зсув у файлі для uprobe */
        __u64 config2;          /* Додаткові параметри raw PMU */
    };

    __u64 branch_sample_type;   /* Бітова маска фільтрації подій LBR */
    __u64 sample_regs_user;     /* Маска CPU-регістрів користувача у вибірці */
    __u32 sample_stack_user;    /* Розмір сирого стеку користувача у вибірці */
    __s32 clockid;              /* Ідентифікатор годинника (CLOCK_MONOTONIC тощо) */
    __u64 sample_regs_intr;     /* Маска регістрів переривання у вибірці */
    __u32 aux_watermark;        /* Поріг водяного знака для AUX буфера */
    __u16 sample_max_stack;     /* Максимальна глибина кадру callchain */
    __u16 __reserved_2;
    __u32 aux_sample_size;      /* Розмір вибірки AUX даних */
    __u32 __reserved_3;
    __u64 sigtrap_data;         /* Пори користувача для SIGTRAP */
};
