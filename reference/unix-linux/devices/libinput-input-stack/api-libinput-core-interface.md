# 📋 Інтерфейс бібліотеки libinput: контексти, події та конфігурація

Бібліотека `libinput` надає низькорівневий інтерфейс мовою C для інтеграції в графічні композитори Wayland, сервери дисплеїв та власні системи керування вводом. Інтерфейс оголошено в заголовному файлі `<libinput.h>`. 

Головне архітектурне завдання інтерфейсу — ізолювати викликача від складнощів системних викликів ядра `ioctl`, розбору бітових масок [evdev](book:unix-linux/input-evdev) та математики фільтрації шумів, надавши натомість строгий об'єктно-орієнтований C-контракт із детермінованою моделлю володіння пам'яттю.

---

## 1. Створення контексту та керування місцями (Seats)

`libinput` не містить коду для відкриття фіксованих шляхів у файловій системі (`/dev/input/event*`). Це фундаментальне безпекове рішення: бібліотека може працювати всередині непривілейованого процесу композитора (без прав суперкористувача `root`). Замість прямого виклику `open()` бібліотека делегує відкриття дескрипторів викликачу через таблицю зворотних викликів `struct libinput_interface`.

```c
struct libinput_interface {
    int  (*open_restricted)(const char *path, int flags, void *user_data);
    void (*close_restricted)(int fd, void *user_data);
};
```

У виробничих композиторах реалізація `open_restricted` надсилає запит до системного демона [systemd-logind](book:unix-linux/logind-sessions-seats) через шину D-Bus (виклик методу `TakeDevice`). Демон `logind` перевіряє, чи належить поточна сесія користувача активному віртуальному терміналу, відкриває файл пристрою з правами root і передає відкритий файловий дескриптор назад композитору через механізм передачі прав `SCM_RIGHTS` у сокеті UNIX.

### Функції життєвого циклу контексту

Контекст `struct libinput` є кореневим об'єктом, що керує пам'яттю, фоновими структурами моніторингу та загальною чергою подій.

| Функція | Призначення, сигнатура та інваріанти |
| :--- | :--- |
| **`libinput_udev_create_context`** | Створює контекст на основі моніторингу підсистеми [udev](book:unix-linux/udev-rules). Використовує клієнтський об'єкт `struct udev *` для автоматичного виявлення пристроїв.<br>`struct libinput *libinput_udev_create_context(const struct libinput_interface *interface, void *user_data, struct udev *udev);` |
| **`libinput_udev_assign_seat`** | Прив'язує контекст до логічного робочого місця (зазвичай `"seat0"`). Сканує наявні пристрої та підписується на події додавання/вилучення udev.<br>`int libinput_udev_assign_seat(struct libinput *libinput, const char *seat_id);` |
| **`libinput_path_create_context`** | Створює автономний контекст без інтеграції з udev. Застосовується в ізольованих тестах та автономних утилітах на кшталт `libinput record`.<br>`struct libinput *libinput_path_create_context(const struct libinput_interface *interface, void *user_data);` |
| **`libinput_path_add_device`** | Вручну реєструє окремий вузол `/dev/input/eventN` у контексті, створеному через `path`.<br>`struct libinput_device *libinput_path_add_device(struct libinput *libinput, const char *path);` |
| **`libinput_ref` / `libinput_unref`** | Атомарне керування лічильником посилань контексту. Коли лічильник досягає нуля, контекст звільняє пам'ять і закриває всі дескриптори через `close_restricted`.<br>`struct libinput *libinput_ref(struct libinput *libinput);`<br>`struct libinput *libinput_unref(struct libinput *libinput);` |

---

## 2. Інтеграція в головний цикл подій

Бібліотека не створює власних фонових потоків виконання (threads) і не є потокобезпечною. Вся робота з контекстом має відбуватися в одному потоці — головному циклі подій композитора. Для взаємодії з механізмами мультиплексування [epoll або poll](book:unix-linux/select-poll-epoll) бібліотека надає єдиний внутрішній файловий дескриптор.

```c
/* Отримання дескриптора сповіщень для реєстрації в epoll/poll з прапорцем EPOLLIN */
int libinput_get_fd(struct libinput *libinput);

/* Зчитування накопичених сирих даних ядра та переведення внутрішніх автоматів станів */
int libinput_dispatch(struct libinput *libinput);

/* Витягування наступної високорівневої події з внутрішньої черги (повертає NULL, якщо черга порожня) */
struct libinput_event *libinput_get_event(struct libinput *libinput);

/* Звільнення пам'яті обробленої події */
void libinput_event_destroy(struct libinput_event *event);
```

### Порядок роботи в циклі обробки

1. Дескриптор, отриманий через `libinput_get_fd()`, реєструється в екземплярі `epoll` з подією `EPOLLIN`.
2. Коли `epoll_wait()` сповіщає про готовність дескриптора, викликач зобов'язаний викликати `libinput_dispatch()`. Ця функція виконує неблокуюче зчитування сирих структур `input_event` з усіх відкритих пристроїв ядра, оновлює автомати станів (фільтри долонь, таймери тапів, балістичні акумулятори) і наповнює чергу готових високорівневих подій.
3. Викликач у циклі `while ((ev = libinput_get_event(li)) != NULL)` вибирає всі події з черги, виконує маршрутизацію вікнам і обов'язково знищує кожну подію через `libinput_event_destroy(ev)`.

---

## 3. Ієрархія типів подій та поліморфні структури

Усі події в бібліотеці представляються непрозорим базовим типом `struct libinput_event`. Базовий тип перевіряється функцією `libinput_event_get_type()` і приводиться до одного зі спеціалізованих підтипів:

```c
enum libinput_event_type {
    LIBINPUT_EVENT_NONE = 0,
    LIBINPUT_EVENT_DEVICE_NOTIFY,           /* Підключено новий пристрій або вилучено наявний */
    
    /* Клавіатурні події */
    LIBINPUT_EVENT_KEYBOARD_KEY = 300,      /* Натискання або відпускання клавіші */
    
    /* Відносний рух вказівника (миша, трекбол) */
    LIBINPUT_EVENT_POINTER_MOTION = 400,    /* Прискорене відносне переміщення курсора */
    LIBINPUT_EVENT_POINTER_MOTION_ABSOLUTE, /* Абсолютне переміщення вказівника */
    LIBINPUT_EVENT_POINTER_BUTTON,          /* Натискання або відпускання фізичної кнопки миші */
    LIBINPUT_EVENT_POINTER_SCROLL_WHEEL,    /* Прокрутка дискретним коліщатком миші */
    LIBINPUT_EVENT_POINTER_SCROLL_FINGER,   /* Прокрутка пальцями по тачпаду */
    LIBINPUT_EVENT_POINTER_SCROLL_CONTINUOUS,/* Неперервна високоточна прокрутка */
    
    /* Прямий сенсорний ввід (тачскрини) */
    LIBINPUT_EVENT_TOUCH_DOWN = 500,        /* Торкання сенсорного скла пальцем у новому слоті */
    LIBINPUT_EVENT_TOUCH_UP,                /* Відривання пальця від поверхні */
    LIBINPUT_EVENT_TOUCH_MOTION,            /* Переміщення контакту по поверхні */
    LIBINPUT_EVENT_TOUCH_CANCEL,            /* Анулювання контакту (перехоплення жестом або долонею) */
    LIBINPUT_EVENT_TOUCH_FRAME,             /* Межа синхронізації одночасних подій мультитачу */
    
    /* Багатопальцеві жести тачпада */
    LIBINPUT_EVENT_GESTURE_SWIPE_BEGIN = 600,/* Початок синхронного свайпу кількома пальцями */
    LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE,    /* Зміна вектора свайпу */
    LIBINPUT_EVENT_GESTURE_SWIPE_END,      /* Завершення свайпу */
    LIBINPUT_EVENT_GESTURE_PINCH_BEGIN,     /* Початок жесту щипка чи обертання */
    LIBINPUT_EVENT_GESTURE_PINCH_UPDATE,    /* Оновлення масштабу та кута щипка */
    LIBINPUT_EVENT_GESTURE_PINCH_END,       /* Завершення щипка */
    LIBINPUT_EVENT_GESTURE_HOLD_BEGIN,      /* Утримання нерухомих пальців на поверхні */
    LIBINPUT_EVENT_GESTURE_HOLD_END,        /* Завершення утримання */
    
    /* Професійні графічні планшети та стилуси */
    LIBINPUT_EVENT_TABLET_TOOL_AXIS = 700,  /* Оновлення координат, тиску чи нахилу пера */
    LIBINPUT_EVENT_TABLET_TOOL_PROXIMITY,   /* Вхід або вихід пера із зони безконтактного зависання */
    LIBINPUT_EVENT_TABLET_TOOL_TIP,         /* Фізичний дотик наконечника пера до планшета */
    LIBINPUT_EVENT_TABLET_TOOL_BUTTON,      /* Натискання клавіш на корпусі самого стилуса */
    LIBINPUT_EVENT_TABLET_PAD_BUTTON = 800, /* Натискання апаратних кнопок на корпусі планшета */
    LIBINPUT_EVENT_TABLET_PAD_RING,         /* Поворот сенсорного кільця на планшеті */
    LIBINPUT_EVENT_TABLET_PAD_STRIP,        /* Рух по лінійній сенсорній смузі планшета */

    /* Апаратні апаратні перемикачі (кришка ноутбука, режим планшета) */
    LIBINPUT_EVENT_SWITCH_TOGGLE = 900,
};
```

---

## 4. Спеціалізовані функції витягування параметрів

### Події вказівника (Pointer Events)

Для подій типу `LIBINPUT_EVENT_POINTER_*` базовий об'єкт перетворюється на покажчик `struct libinput_event_pointer *` за допомогою функції `libinput_event_get_pointer_event()`.

```c
struct libinput_event_pointer *libinput_event_get_pointer_event(struct libinput_event *event);

/* Прискорені балістичні дельти переміщення в пікселях робочого столу */
double libinput_event_pointer_get_dx(struct libinput_event_pointer *event);
double libinput_event_pointer_get_dy(struct libinput_event_pointer *event);

/* Фізичні неприскорені зміщення (у міліметрах) для шутерів від першої особи та САПР */
double libinput_event_pointer_get_dx_unaccelerated(struct libinput_event_pointer *event);
double libinput_event_pointer_get_dy_unaccelerated(struct libinput_event_pointer *event);

/* Номер кнопки за стандартом Linux (BTN_LEFT = 272, BTN_RIGHT = 273, BTN_MIDDLE = 274) */
uint32_t libinput_event_pointer_get_button(struct libinput_event_pointer *event);
enum libinput_button_state libinput_event_pointer_get_button_state(struct libinput_event_pointer *event);

/* Значення прокрутки по осях LIBINPUT_POINTER_AXIS_SCROLL_VERTICAL або HORIZONTAL */
double libinput_event_pointer_get_scroll_value(struct libinput_event_pointer *event,
                                               enum libinput_pointer_axis axis);
/* Значення прокрутки під стандартом v120 (120 одиниць = 1 дискретний клік звичайного колеса) */
double libinput_event_pointer_get_scroll_value_v120(struct libinput_event_pointer *event,
                                                    enum libinput_pointer_axis axis);
```

### Події жестів тачпада (Gesture Events)

Події жестів транслюють оброблені вектори руху цілої групи пальців.

```c
struct libinput_event_gesture *libinput_event_get_gesture_event(struct libinput_event *event);

/* Кількість одночасно задіяних пальців у поточному жесті (3 або 4 для свайпу; 2, 3 або 4 для щипка) */
int libinput_event_gesture_get_finger_count(struct libinput_event_gesture *event);

/* Зміщення центру мас групи пальців відносно попереднього кадру події */
double libinput_event_gesture_get_dx(struct libinput_event_gesture *event);
double libinput_event_gesture_get_dy(struct libinput_event_gesture *event);

/* Масштабний множник: 1.0 — початковий стан, >1.0 — розведення пальців, <1.0 — стискання */
double libinput_event_gesture_get_scale(struct libinput_event_gesture *event);

/* Кутова дельта повороту лінії між пальцями (у градусах, позитивне значення — за годинниковою стрілкою) */
double libinput_event_gesture_get_angle_delta(struct libinput_event_gesture *event);
```

### Події графічного планшета (Tablet Tool Events)

Планшетні події несуть повну фізичну інформацію про положення бездротового стилуса у тривимірному просторі над сенсорною поверхнею.

```c
struct libinput_event_tablet_tool *libinput_event_get_tablet_tool_event(struct libinput_event *event);

/* Нормалізована сила притискання наконечника до скла планшета в діапазоні [0.0, 1.0] */
double libinput_event_tablet_tool_get_pressure(struct libinput_event_tablet_tool *event);

/* Кути просторового нахилу пера у градусах відносно площини сенсора (зазвичай [-60.0, +60.0]) */
double libinput_event_tablet_tool_get_tilt_x(struct libinput_event_tablet_tool *event);
double libinput_event_tablet_tool_get_tilt_y(struct libinput_event_tablet_tool *event);

/* Висота безконтактного зависання пера над поверхнею планшета у діапазоні [0.0, 1.0] */
double libinput_event_tablet_tool_get_distance(struct libinput_event_tablet_tool *event);

/* Кут обертання пера довкола своєї поздовжньої осі (для симуляції каліграфічних плоских пензлів [0.0, 360.0]) */
double libinput_event_tablet_tool_get_rotation(struct libinput_event_tablet_tool *event);
```

---

## 5. Модель об'єктного зв'язування та групування пристроїв

Сучасні пристрої вводу часто складаються з кількох логічних вузлів ядра. Наприклад, графічний планшет Wacom створює окремий вузол `/dev/input/eventA` для сенсорної поверхні пера та `/dev/input/eventB` для апаратних кнопок планшета (Tablet Pad). Клавіатура ноутбука та вбудований трекпойнт також представлені різними дескрипторами, хоча фізично розташовані в одному корпусі.

Для вирішення цієї проблеми `libinput` надає механізм **логічних груп пристроїв (`struct libinput_device_group`)**:

```c
/* Отримання групи, до якої належить пристрій */
struct libinput_device_group *libinput_device_get_device_group(struct libinput_device *device);

/* Керування часом життя групи через підрахунок посилань */
struct libinput_device_group *libinput_device_group_ref(struct libinput_device_group *group);
struct libinput_device_group *libinput_device_group_unref(struct libinput_device_group *group);
```

Всі пристрої, що мають однаковий ідентифікатор групи, розглядаються бібліотекою як єдиний апаратний комплекс. Саме завдяки цьому механізму функція блокування тачпада при наборі тексту (DWT) знає, яка саме клавіатура спарена з тачпадом, і не блокує вбудовану сенсорну панель при натисканні клавіш на зовнішній бездротовій USB-клавіатурі.

### Часові мітки та монотонні годинники

Кожна подія у `libinput` містить мікросекундну мітку часу:

```c
uint64_t libinput_event_get_time_usec(struct libinput_event *event);
```

Час обчислюється виключно за системним монотонним годинником ядра `CLOCK_MONOTONIC`. Це гарантує, що ручне переведення системного стінного годинника користувачем (або синхронізація через NTP) ніколи не зламає внутрішні таймери тачпадних тапів, детектора подвійного кліку чи фільтрів швидкості прискорення.

### Апаратні перемикачі (Switch Events)

Ноутбуки та конвертовані пристрої «2-в-1» обладнані датчиками положення кришки та повороту екрана:

```c
struct libinput_event_switch *libinput_event_get_switch_event(struct libinput_event *event);
enum libinput_switch libinput_event_switch_get_switch(struct libinput_event_switch *event);
enum libinput_switch_state libinput_event_switch_get_switch_state(struct libinput_event_switch *event);
```

Константа `LIBINPUT_SWITCH_LID` сигналізує про закриття чи відкриття кришки ноутбука, а `LIBINPUT_SWITCH_TABLET_MODE` повідомляє композитору про розгортання екрана на 360° у режим планшета. Отримавши сигнал переходу в режим планшета, композитор автоматично вимикає обробку вводу з фізичної клавіатури й тачпада, щоб уникнути паразитарних натискань клавіш на тильному боці пристрою, та показує віртуальну екранну клавіатуру.

---

## 6. Програмне конфігурування пристроїв

Всі параметри роботи пристроїв керуються динамічно через дескриптор `struct libinput_device *`. Функції повертають статус виконання `enum libinput_config_status`:

- `LIBINPUT_CONFIG_STATUS_SUCCESS` (0) — налаштування успішно застосовано;
- `LIBINPUT_CONFIG_STATUS_UNSUPPORTED` — функція не підтримується апаратним забезпеченням цього пристрою;
- `LIBINPUT_CONFIG_STATUS_INVALID` — передано некоректні числові параметри за межами допустимого діапазону.

### Зведена таблиця API конфігурації

| Область налаштування | Сигнатури функцій та приклади значень |
| :--- | :--- |
| **Tap-to-click** | `enum libinput_config_status libinput_device_config_tap_set_enabled(struct libinput_device *dev, enum libinput_config_tap_state enable);`<br>`libinput_device_config_tap_set_button_map(dev, LIBINPUT_CONFIG_TAP_MAP_LRM);`<br>*(LRM: 1 палець = Left Click, 2 = Right, 3 = Middle)* |
| **Прискорення вказівника** | `libinput_device_config_accel_set_profile(dev, LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE);`<br>`libinput_device_config_accel_set_speed(dev, 0.2);`<br>*(швидкість у діапазоні від -1.0 [максимальне уповільнення] до +1.0 [максимальне прискорення])* |
| **Блокування при наборі (DWT)** | `libinput_device_config_dwt_set_enabled(dev, LIBINPUT_CONFIG_DWT_ENABLED);`<br>*(автоматично блокує тачпад на 500 мс після кожного натискання літерної клавіші)* |
| **Метод прокрутки** | `libinput_device_config_scroll_set_method(dev, LIBINPUT_CONFIG_SCROLL_2FG);`<br>`libinput_device_config_scroll_set_natural_scroll_enabled(dev, 1);`<br>*(1 — рух документа слідує за пальцями; 0 — класичний напрямок смуги прокрутки)* |
| **Матриця калібрування** | `libinput_device_config_calibration_set_matrix(dev, const float matrix[6]);`<br>*(передає коефіцієнти афінного перетворення 3 × 3 для виправлення повороту, зміщення чи масштабування екрана)* |

### Керування користувацькими профілями прискорення

Починаючи з версії 1.19, `libinput` дозволяє створювати довільні нелінійні криві прискорення миші за допомогою API користувацьких профілів:

```c
struct libinput_config_accel *libinput_config_accel_create_custom_profile(void);
enum libinput_config_status libinput_config_accel_set_points(
    struct libinput_config_accel *config,
    size_t npoints,
    const double *speeds,
    const double *accel_factors);
```

Композитор передає масив опорних точок `speeds` (швидкість руки у мм/с) та відповідні значення `accel_factors`. Бібліотека інтерполює проміжні значення кубічним сплайном, що дозволяє користувачам налаштовувати унікальні балістичні профілі під власні потреби.

### Збереження конфігурації до підключення пристроїв

Важливою особливістю архітектури є те, що `libinput` не зберігає налаштування на диску у власних конфігураційних файлах. Бібліотека є чистим виконавчим механізмом простору користувача. Графічне середовище (наприклад, GNOME Settings або KDE System Settings) зберігає вибір користувача у власній системі налаштувань (GSettings або KConfig), а композитор застосовує ці параметри через функції `libinput_device_config_*` у момент отримання події `LIBINPUT_EVENT_DEVICE_NOTIFY` під час гарячого підключення пристрою.
