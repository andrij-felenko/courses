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
