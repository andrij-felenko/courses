struct pvclock_vcpu_time_info {
    uint32_t version;
    uint32_t pad0;
    uint64_t tsc_timestamp;     /* Значення TSC хоста */
    uint64_t system_time;       /* Відповідний наносекундний час хоста */
    uint32_t tsc_to_system_mul; /* Коефіцієнт масштабування тактів */
    int8_t   tsc_shift;         /* Зсув ділення */
    uint8_t  flags;             /* Прапорці стабільності */
    uint8_t  pad[2];
};
