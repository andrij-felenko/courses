# Проєкт: Власний Thermal Governor (Концепт)

Розробка власного алгоритму терморегуляції (Thermal Governor) вимагає знання API теплового каркаса в ядрі Linux. Дві речі варто з'ясувати ще до першого рядка коду.

**Перше: регулятор не збирається окремим модулем.** Функція `thermal_register_governor()` живе всередині `drivers/thermal/thermal_core.c`, назовні не експортується (`EXPORT_SYMBOL` для неї немає) і видима лише коду самого каркаса. Усі регулятори вбудовані в тепловий каркас, а до його списку потрапляють через таблицю в окремій секції компонувальника, яку заповнює макрос `THERMAL_GOVERNOR_DECLARE()` (`drivers/thermal/thermal_core.h`). Тож «власний регулятор» — це файл поруч із `gov_step_wise.c` плюс рядок у `Kconfig` і `Makefile`, а не `insmod`.

**Друге: набір колбеків залежить від версії ядра.** У ядрах до 6.9 включно `struct thermal_governor` була публічною (`include/linux/thermal.h`) і мала колбек `int (*throttle)(struct thermal_zone_device *tz, const struct thermal_trip *trip)`. У 6.10 інтерфейс перероблено: структуру перенесено в приватний заголовок `drivers/thermal/thermal_core.h`, `.throttle` прибрано, а на його місце стало два колбеки — `.trip_crossed()` (виклик у момент перетину конкретного порога, з ознакою напрямку) і `.manage()` (виклик на кожне оновлення температури, коли регулятор переглядає зону цілком). Step-Wise, Fair-Share і Power Allocator переведено на `.manage()`; Bang-Bang, як термостат за подіями, лишився на `.trip_crossed()`. Огляд самої переробки — [LWN, «thermal: core: Redesign the governor interface»](https://lwn.net/Articles/969476/).

Найменший регулятор під сучасний інтерфейс (форма ядра 6.10) виглядає так:

```c
#include <linux/thermal.h>
#include "thermal_core.h"

static void custom_trip_crossed(struct thermal_zone_device *tz,
                                const struct thermal_trip *trip,
                                bool upward)
{
    struct thermal_instance *instance;

    if (trip->type != THERMAL_TRIP_ACTIVE)
        return;

    /* прив'язки «зона — пристрій охолодження», зроблені cooling-maps */
    list_for_each_entry(instance, &tz->thermal_instances, tz_node) {
        if (instance->trip != trip)
            continue;

        instance->target = upward ? instance->upper : instance->lower;
        instance->initialized = true;
        thermal_cdev_update(instance->cdev);
    }
}

static struct thermal_governor thermal_gov_custom = {
    .name         = "custom_gov",
    .trip_crossed = custom_trip_crossed,
};
THERMAL_GOVERNOR_DECLARE(thermal_gov_custom);
```

Тут регулятор нічого не опитує: ядро саме кличе `custom_trip_crossed()`, коли температура перетнула поріг, і повідомляє напрям (`upward`). Для алгоритму, якому потрібна вся картина, а не одна подія, місце логіки — `.manage()`: його кличуть на кожне оновлення температури зони, і він може обійти всі пороги через `for_each_trip_desc()`.

Одне застереження щодо коду: перелік прив'язок — деталь внутрішньої будови, і вона рухається. У 6.10 список лежить у зоні (`tz->thermal_instances`, вузол `tz_node`), у пізніших випусках його перенесено ближче до порога (`td->thermal_instances`, вузол `trip_node`, як у теперішньому `gov_bang_bang.c`). Перед збиранням варто звірити поля з `drivers/thermal/thermal_core.h` саме своєї версії.
