/* Ініціалізація середовища DSM, пулу двійників та обробника SIGSEGV */
dsm_status_t dsm_init(const dsm_config_t *config);

/* Виділення спільного діапазону пам'яті */
void* dsm_alloc_shared(size_t size_bytes);

/* Звільнення виділеної спільної пам'яті */
void dsm_free_shared(void *ptr);

/* Демонтаж середовища DSM та відновлення системних обробників сигналів */
void dsm_destroy(void);
