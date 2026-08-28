struct gendisk {
    int major;                        // Старший номер пристрою
    int first_minor;                  // Перший молодший номер
    int minors;                       // Максимальна кількість розділів (наприклад, 16)
    char disk_name[DISK_NAME_LEN];    // Назва диска у /dev (наприклад, "sda")
    
    const struct block_device_operations *fops; // Таблиця операцій диска
    struct request_queue *queue;      // Черга запитів I/O (blk-mq)
    void *private_data;               // Вказівник на приватні дані драйвера
    unsigned long state;              // Бітові прапорці стану диска (GD_NEED_PART_SCAN тощо)
};
