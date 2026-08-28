struct counter_watch {
    struct counter_component component;
    __u32 event;
    __u8 channel;
};

struct counter_event {
    __u64 timestamp;  /* Час виникнення події u64 (CLOCK_MONOTONIC, нс) */
    __u64 value;      /* 64-бітне значення лічильника на момент події */
    __u8 watch_id;    /* Унікальний ID спостерігача, призначений ядром */
    __u8 channel;     /* Номер апаратного каналу */
    __u8 pad[6];      /* Явне вирівнювання структури до 24 байтів */
};
