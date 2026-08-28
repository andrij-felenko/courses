// Виділення структури gendisk із вказаною кількістю мінорних номерів.
// До ядра 5.15 — саме так; від 5.15 диск створюють разом із чергою
// виклики blk_alloc_disk() / blk_mq_alloc_disk().
struct gendisk *alloc_gendisk(int minors);

// Додавання диска в систему (робить диск видимим у sysfs та /dev)
int add_disk(struct gendisk *disk);

// Видалення диска із системи (деактивація розділів та черг)
void del_gendisk(struct gendisk *gp);

// Зменшення лічильника посилань на gendisk та звільнення пам'яті
void put_disk(struct gendisk *disk);
