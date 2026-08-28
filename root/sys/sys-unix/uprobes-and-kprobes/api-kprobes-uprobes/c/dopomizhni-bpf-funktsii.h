/* Читання пам'яті ядра у буфер BPF-програми */
long bpf_probe_read_kernel(void *dst, u32 size, const void *unsafe_ptr);

/* Читання рядка з пам'яті ядра */
long bpf_probe_read_kernel_str(void *dst, u32 size, const void *unsafe_ptr);

/* Читання пам'яті простору користувача (Ring 3) */
long bpf_probe_read_user(void *dst, u32 size, const void *unsafe_ptr);

/* Читання рядка з простору користувача */
long bpf_probe_read_user_str(void *dst, u32 size, const void *unsafe_ptr);

/* Отримання поточного ідентифікатора процесу (PID у старших 32 бітах, TGID у молодших) */
u64 bpf_get_current_pid_tgid(void);

/* Отримання назви поточного процесу (comm) */
long bpf_get_current_comm(void *buf, u32 size_of_buf);
