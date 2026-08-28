#include <linux/pm_wakeup.h>

/* Ініціалізує внутрішній об'єкт wakeup_source та вмикає/вимикає пробудження */
int device_init_wakeup(struct device *dev, bool enable);

/* Встановлює апаратну здатність пристрою будити платформу */
void device_set_wakeup_capable(struct device *dev, bool capable);

/* Вмикає або вимикає генерацію подій пробудження для пристрою */
int device_set_wakeup_enable(struct device *dev, bool enable);

/* Перевіряє, чи пристрій увімкнено як активне джерело пробудження */
bool device_may_wakeup(struct device *dev);
