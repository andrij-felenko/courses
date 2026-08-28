struct kvm_run {
    /* Вхідні прапори користувацького простору */
    __u8 request_interrupt_window; // 1 = вийти з KVM_RUN, щойно гість буде готовий прийняти переривання
    __u8 immediate_exit;           // 1 = негайно перервати KVM_RUN
    __u8 padding1[6];

    /* Вихідні дані ядра */
    __u32 exit_reason;             // Код причини виходу з гостьового режиму
    __u8 ready_for_interrupt_injection;
    __u8 if_flag;                  // Стан прапора IF гостя
    __u16 flags;
    __u64 cr8;
    __u64 apic_base;

    /* Об'єднання (union) параметрів залежно від exit_reason */
    union {
        /* KVM_EXIT_IO: Емуляція портів введення-виведення (IN / OUT) */
        struct {
            __u8 direction;    // KVM_EXIT_IO_IN (0) або KVM_EXIT_IO_OUT (1)
            __u8 size;         // Розмір операції в байтах (1, 2, 4)
            __u16 port;        // Номер порту I/O (наприклад, 0x3F8)
            __u32 count;       // Кількість елементів для рядкових інструкцій (INS/OUTS)
            __u64 data_offset; // Зсув в байтах від початку структури kvm_run до буфера даних
        } io;

        /* KVM_EXIT_MMIO: Емуляція пам'яті пристроїв */
        struct {
            __u64 phys_addr;   // GPA адреса, до якої звернувся гість
            __u8  data[8];     // Буфер для прочитаних або записаних байтів
            __u32 len;         // Довжина операції (1..8 байтів)
            __u8  is_write;    // 1 = запис у пристрій, 0 = читання з пристрою
        } mmio;

        /* KVM_EXIT_FAIL_ENTRY: Апаратний збій інструкції VMLAUNCH/VMRESUME */
        struct {
            __u64 hardware_entry_failure_reason; // Апаратний код помилки Intel/AMD
            __u32 cpu;
        } fail_entry;

        /* KVM_EXIT_INTERNAL_ERROR: Внутрішній збій ядра KVM */
        struct {
            __u32 suberror;
            __u32 ndata;
            __u64 data[16];
        } internal;

        /* KVM_EXIT_SYSTEM_EVENT: Запит на перезавантаження або вимкнення */
        struct {
            __u32 type;        // KVM_SYSTEM_EVENT_SHUTDOWN, RESET, CRASH
            __u64 flags;
        } system_event;
    };
};
