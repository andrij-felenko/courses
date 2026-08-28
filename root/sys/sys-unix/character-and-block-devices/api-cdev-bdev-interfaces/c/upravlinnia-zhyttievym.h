// Динамічне виділення діапазону номерів пристроїв (ядро сама обирає вільний Major)
int alloc_chrdev_region(dev_t *dev, unsigned baseminor, unsigned count, const char *name);

// Статична реєстрація заздалегідь відомого діапазону номерів
int register_chrdev_region(dev_t from, unsigned count, const char *name);

// Звільнення раніше виділеного діапазону номерів пристроїв
void unregister_chrdev_region(dev_t from, unsigned count);

// Ініціалізація структури cdev та зв'язування з file_operations
void cdev_init(struct cdev *cdev, const struct file_operations *fops);

// Виділення пам'яті під cdev на купі ядра (динамічний спосіб)
struct cdev *cdev_alloc(void);

// Додавання cdev до системи (робить пристрій активним для системних викликів VFS)
int cdev_add(struct cdev *p, dev_t dev, unsigned count);

// Видалення cdev із системи (деактивація перед деініціалізацією драйвера)
void cdev_del(struct cdev *p);
