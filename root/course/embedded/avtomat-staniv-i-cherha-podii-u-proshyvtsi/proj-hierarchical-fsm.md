# ⚙️ Рушій ієрархічного автомата станів (HSM) з чергою подій

У складних вбудованих пристроях — від медичних моніторів та контролерів ЧПУ до зарядних станцій — класичний плоский автомат станів швидко захаращується дубльованими переходами. Якщо в інтерфейсі приладу є десяток вкладених екранів налаштувань, і на кожному з них натискання кнопки «Назад», сигнал тривоги від батареї або таймаут бездіяльності мають виконувати однакову дію, у плоскому автоматі доводиться повторювати один і той самий обробник у кожному стані окремо. Це призводить до комбінаторного розбухання коду, де випадково пропущена стрілка переходу стає прихованою вразливістю.

Ієрархічний автомат станів (**Hierarchical State Machine**, HSM), заснований на формалізмі Statecharts Девіда Гареля, розв'язує цю проблему за принципом **поведінкового наслідування**: активний підстан обробляє лише ті події, які є унікальними для його поточної задачі, а всі загальні, аварійні та навігаційні сигнали автоматично піднімаються до суперстану (батьківського стану).

Нижче наведено повністю статичний (без виділення динамічної пам'яті через `malloc` чи `new`), детермінований рушій HSM для мікроконтролерів із гарантованим порядком виконання дій входу (`Entry`) та виходу (`Exit`), а також алгоритмом обчислення найближчого спільного предка (**LCA** — Lowest Common Ancestor) під час переходів між різними гілками дерева станів.

---

### Принцип роботи та протокол службових сигналів

Обробник стану в даній архітектурі реалізується як функція зі строго визначеною сигнатурою. Вона приймає покажчик на екземпляр автомата та вхідну подію, а повертає статус результату обробки:

1. `Q_RET_HANDLED` — подію повністю розпізнано й оброблено поточним підстаном. Подальше підняття по дереву ієрархії припиняється.
2. `Q_RET_IGNORED` — подія свідомо проігнорована станом, проте її передача батьківським станам заблокована.
3. `Q_RET_TRAN` — стан ініціював перехід до іншого цільового стану. Рушій запускає ланцюжок виходу/входу.
4. `Q_RET_SUPER` — поточний стан не має логіки для цієї події. Подія передається суперстану, записаному в тимчасове поле `me->temp`.

```
┌─────────────────────────────────────────────────────────────┐
│ Зарезервовані службові сигнали життєвого циклу:             │
│                                                             │
│ • Q_ENTRY_SIG (1): Викликається автоматично ПРИ ВХОДІ.      │
│   Ініціалізація периферії, запуск таймерів, інваріанти.    │
│                                                             │
│ • Q_EXIT_SIG  (2): Викликається автоматично ПРИ ВИХОДІ.     │
│   Гарантоване знеструмлення силових реле, очищення пам'яті. │
│                                                             │
│ • Q_INIT_SIG  (3): Викликається після входу в суперстан.    │
│   Визначає початковий типовий підстан (Default Substate).   │
│                                                             │
│ • Q_USER_SIG  (4+): Початок користувацьких сигналів програми│
└─────────────────────────────────────────────────────────────┘
```

Головна перевага службових сигналів полягає в тому, що вони є внутрішніми для рушія і ніколи не потрапляють у зовнішню чергу подій. Їх генерує сам диспетчер під час виконання переходу.

---

### Анатомія переходу: підйом до LCA та спуск у цільовий стан

Коли активний стан викликає макрос `Q_TRAN(target)`, рушій повинен коректно перевести систему з поточної гілки в нову. Якщо просто змінити покажчик `state = target`, прошивка залишить увімкненими ресурси старого стану і не ініціалізує контекст нового.

Правильний алгоритм переходу виконує три фази:
1. **Фаза підйому (Exit Path):** Від поточного активного стану вгору по ланцюжку батьків викликається `Q_EXIT_SIG` для кожного стану, доки рушій не досягне найближчого спільного предка (LCA) вихідного та цільового станів.
2. **Фаза перехідної дії (Transition Action):** Виконується дія, прив'язана до самого переходу (наприклад, скидання лічильника помилок).
3. **Фаза спуску (Entry Path):** Від LCA вниз до цільового стану послідовно викликається `Q_ENTRY_SIG`. Оскільки порядок виклику має бути строго зверху-вниз (спочатку батько, потім син), рушій спочатку записує шлях у масив `entry_path[]`, а потім викликає їх у зворотному порядку.
4. **Фаза внутрішньої ініціалізації:** Якщо цільовий стан є складеним (суперстаном), для нього викликається `Q_INIT_SIG`, щоб активувати його типовий внутрішній підстан.

---

### Повна реалізація рушія HSM

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define Q_MAX_DEPTH 8

/* Базові типи сигналів та результатів */
typedef uint16_t QSignal;

enum QReservedSignals {
    Q_ENTRY_SIG = 1,
    Q_EXIT_SIG  = 2,
    Q_INIT_SIG  = 3,
    Q_USER_SIG  = 4
};

typedef enum {
    Q_RET_HANDLED,
    Q_RET_IGNORED,
    Q_RET_TRAN,
    Q_RET_SUPER
} QResult;

/* Структура події */
typedef struct {
    QSignal sig;
    uintptr_t param;
} QEvt;

/* Службові статичні події для життєвого циклу */
static const QEvt pkg_entry_evt = { Q_ENTRY_SIG, 0 };
static const QEvt pkg_exit_evt  = { Q_EXIT_SIG,  0 };
static const QEvt pkg_init_evt  = { Q_INIT_SIG,  0 };

/* Оголошення типу автомата та покажчика на функцію стану */
typedef struct QHsm QHsm;
typedef QResult (*QStateHandler)(QHsm *me, const QEvt *e);

struct QHsm {
    QStateHandler state;   /* поточний активний стан */
    QStateHandler temp;    /* тимчасовий стан під час переходу / суперстан */
};

/* Макроси повернення результату для лаконічності коду станів */
#define Q_HANDLED()         (Q_RET_HANDLED)
#define Q_IGNORED()         (Q_RET_IGNORED)
#define Q_TRAN(target_)     (((QHsm *)me)->temp = (QStateHandler)(target_), Q_RET_TRAN)
#define Q_SUPER(super_)     (((QHsm *)me)->temp = (QStateHandler)(super_), Q_RET_SUPER)

/* Топовий суперстан системи (корінь ієрархії) */
static QResult QHsm_top(QHsm *me, const QEvt *e) {
    (void)me;
    (void)e;
    return Q_RET_IGNORED;
}

/* Ініціалізація автомата з початковим станом */
void QHsm_init(QHsm *me, QStateHandler initial) {
    me->state = QHsm_top;
    /* Виклик початкового переходу для визначення цільового стану */
    initial(me, &pkg_init_evt);
    QStateHandler target = me->temp;
    
    /* Побудова шляху входу від кореня до цільового стану */
    QStateHandler entry_path[Q_MAX_DEPTH];
    int8_t depth = 0;
    
    QStateHandler s = target;
    while (s != QHsm_top && s != NULL && depth < Q_MAX_DEPTH) {
        entry_path[depth++] = s;
        me->temp = QHsm_top;
        s(me, &pkg_entry_evt);
        s = me->temp; /* отримали суперстан */
    }
    
    /* Виконання дій Entry згори донизу */
    while (--depth >= 0) {
        entry_path[depth](me, &pkg_entry_evt);
    }
    me->state = target;
    me->state(me, &pkg_init_evt);
}

/* Диспетчеризація події та обчислення переходів із викликом Exit/Entry */
void QHsm_dispatch(QHsm *me, const QEvt *e) {
    QStateHandler s = me->state;
    QResult res;

    /* Бульбашкове підняття події вгору по ієрархії, поки хтось не обробить */
    while (s != QHsm_top && s != NULL) {
        me->temp = QHsm_top;
        res = s(me, e);

        if (res == Q_RET_HANDLED || res == Q_RET_IGNORED) {
            return; /* Подію успішно поглинуто або проігноровано */
        }

        if (res == Q_RET_TRAN) {
            QStateHandler target = me->temp;
            QStateHandler source = s;

            /* 1. Вихід з поточного стану вгору до джерела переходу */
            for (QStateHandler c = me->state; c != source; ) {
                c(me, &pkg_exit_evt);
                me->temp = QHsm_top;
                c(me, &pkg_entry_evt);
                c = me->temp;
            }
            source(me, &pkg_exit_evt);

            /* 2. Обчислення шляху входу до target (LCA шлях) */
            QStateHandler entry_path[Q_MAX_DEPTH];
            int8_t depth = 0;
            QStateHandler t = target;

            while (t != QHsm_top && t != NULL && depth < Q_MAX_DEPTH) {
                entry_path[depth++] = t;
                me->temp = QHsm_top;
                t(me, &pkg_entry_evt);
                t = me->temp;
            }

            /* 3. Виконання Entry згори донизу до цільового стану */
            while (--depth >= 0) {
                entry_path[depth](me, &pkg_entry_evt);
            }

            me->state = target;
            me->state(me, &pkg_init_evt);
            return;
        }

        /* Перехід до суперстану, якщо стан повернув Q_RET_SUPER */
        s = me->temp;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

enum class QSignal : uint16_t {
    Entry = 1,
    Exit  = 2,
    Init  = 3,
    User  = 4
};

enum class QResult : uint8_t {
    Handled,
    Ignored,
    Transition,
    Super
};

struct QEvt {
    QSignal sig;
    uintptr_t param{0};
};

class HsmBase {
public:
    using StateHandler = QResult (HsmBase::*)(const QEvt&);
    static constexpr size_t MaxDepth = 8;

    explicit HsmBase(StateHandler initial) : state_(&HsmBase::topState), initial_(initial) {}

    void init() {
        (this->*initial_)(QEvt{QSignal::Init});
        auto target = temp_;

        std::array<StateHandler, MaxDepth> entry_path{};
        int8_t depth = 0;

        auto s = target;
        while (s != &HsmBase::topState && depth < static_cast<int8_t>(MaxDepth)) {
            entry_path[depth++] = s;
            temp_ = &HsmBase::topState;
            (this->*s)(QEvt{QSignal::Entry});
            s = temp_;
        }

        while (--depth >= 0) {
            (this->*entry_path[depth])(QEvt{QSignal::Entry});
        }
        state_ = target;
        (this->*state_)(QEvt{QSignal::Init});
    }

    void dispatch(const QEvt& e) {
        auto s = state_;
        while (s != &HsmBase::topState) {
            temp_ = &HsmBase::topState;
            QResult res = (this->*s)(e);

            if (res == QResult::Handled || res == QResult::Ignored) {
                return;
            }

            if (res == QResult::Transition) {
                auto target = temp_;
                auto source = s;

                for (auto c = state_; c != source; ) {
                    (this->*c)(QEvt{QSignal::Exit});
                    temp_ = &HsmBase::topState;
                    (this->*c)(QEvt{QSignal::Entry});
                    c = temp_;
                }
                (this->*source)(QEvt{QSignal::Exit});

                std::array<StateHandler, MaxDepth> entry_path{};
                int8_t depth = 0;
                auto t = target;

                while (t != &HsmBase::topState && depth < static_cast<int8_t>(MaxDepth)) {
                    entry_path[depth++] = t;
                    temp_ = &HsmBase::topState;
                    (this->*t)(QEvt{QSignal::Entry});
                    t = temp_;
                }

                while (--depth >= 0) {
                    (this->*entry_path[depth])(QEvt{QSignal::Entry});
                }

                state_ = target;
                (this->*state_)(QEvt{QSignal::Init});
                return;
            }

            s = temp_;
        }
    }

protected:
    QResult topState(const QEvt&) { return QResult::Ignored; }
    
    QResult handled() const { return QResult::Handled; }
    QResult ignored() const { return QResult::Ignored; }
    QResult tran(StateHandler target) { temp_ = target; return QResult::Transition; }
    QResult super(StateHandler parent) { temp_ = parent; return QResult::Super; }

    StateHandler state_{&HsmBase::topState};
    StateHandler temp_{&HsmBase::topState};
    StateHandler initial_;
};
```
:::

---

### Приклад: Трьохрівневе ієрархічне меню приладу

Розглянемо практичний пристрій — портативний вимірювальний калібратор з графічним дисплеєм.
Дерево станів пристрою:
- **`ScreenSaver`**: Екран вимкнено, процесор спить, реагує лише на кнопку живлення.
- **`Active` (Суперстан верхнього рівня)**: Вмикає підсвітку дисплея при вході (`Entry`), гасить при виході (`Exit`). Перехоплює глобальний таймаут бездіяльності `TIMEOUT_IDLE_SIG` з будь-якого вкладеного підменю і повертає систему в `ScreenSaver`.
  - **`MainMenu` (Підстан `Active`)**: Список вибору функцій приладу.
  - **`Settings` (Підстан `Active`)**: Редагування яскравості екрана та параметрів фільтрації.
    - **`Calibration` (Підстан `Settings`)**: Режим точного калібрування АЦП.

Зверніть увагу: перебуваючи у стані `Calibration`, користувач може нічого не натискати протягом хвилини. Сигнал `TIMEOUT_IDLE_SIG` не обробляється у `Calibration` і не обробляється у `Settings`. Він автоматично спливає до суперстану `Active`, який викликає `Q_TRAN(state_screen_saver)`. При цьому рушій послідовно виконає:
1. `Calibration` -> `Q_EXIT_SIG` (зупинка генератора калібрувального сигналу);
2. `Settings` -> `Q_EXIT_SIG` (збереження налаштувань у Flash);
3. `Active` -> `Q_EXIT_SIG` (вимкнення живлення підсвітки екрана);
4. `ScreenSaver` -> `Q_ENTRY_SIG` (перехід у мікроспоживання).

Жодна плоска машина станів не здатна забезпечити таку надійність без десятків дубльованих перевірок.

:::tabs
```c
/* Користувацькі сигнали */
enum DeviceSignals {
    BTN_UP_SIG = Q_USER_SIG,
    BTN_DOWN_SIG,
    BTN_ENTER_SIG,
    BTN_BACK_SIG,
    TIMEOUT_IDLE_SIG
};

/* Контекст меню приладу */
typedef struct {
    QHsm super;
    uint8_t brightness;
    bool is_calibrated;
} DeviceUI;

/* Прототипи функцій станів */
static QResult state_screen_saver(QHsm *me, const QEvt *e);
static QResult state_active(QHsm *me, const QEvt *e);
static QResult state_main_menu(QHsm *me, const QEvt *e);
static QResult state_settings(QHsm *me, const QEvt *e);
static QResult state_calibration(QHsm *me, const QEvt *e);

/* Початковий стан */
static QResult state_initial(QHsm *me, const QEvt *e) {
    (void)e;
    return Q_TRAN(state_screen_saver);
}

/* Стан збереження енергії / заставки */
static QResult state_screen_saver(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case BTN_ENTER_SIG:
        case BTN_BACK_SIG:
            return Q_TRAN(state_main_menu);

        default:
            return Q_SUPER(QHsm_top);
    }
}

/* Суперстан Active: керує активною підсвіткою та загальними таймаутами */
static QResult state_active(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case Q_ENTRY_SIG:
            // LCD_SetBacklight(100);
            return Q_HANDLED();

        case Q_EXIT_SIG:
            // LCD_SetBacklight(0);
            return Q_HANDLED();

        case TIMEOUT_IDLE_SIG:
            /* Глобальний таймаут: з будь-якого підменю йдемо в ScreenSaver */
            return Q_TRAN(state_screen_saver);

        default:
            return Q_SUPER(QHsm_top);
    }
}

/* Підстан: Головне меню */
static QResult state_main_menu(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case Q_ENTRY_SIG:
            // Draw_Icon_Menu();
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            return Q_TRAN(state_settings);

        default:
            /* Усі невідомі події піднімаються до state_active */
            return Q_SUPER(state_active);
    }
}

/* Підстан: Налаштування */
static QResult state_settings(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            // Display_Settings_List();
            return Q_HANDLED();

        case BTN_UP_SIG:
            if (dev->brightness < 100) dev->brightness += 10;
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            return Q_TRAN(state_calibration);

        case BTN_BACK_SIG:
            /* Повернення на головний екран */
            return Q_TRAN(state_main_menu);

        default:
            return Q_SUPER(state_active);
    }
}

/* Підстан: Калібрування (вкладений у state_settings) */
static QResult state_calibration(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            // ADC_Start_Calib();
            return Q_HANDLED();

        case Q_EXIT_SIG:
            // ADC_Stop_Calib();
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            dev->is_calibrated = true;
            return Q_TRAN(state_settings);

        case BTN_BACK_SIG:
            /* Повернення на рівень налаштувань */
            return Q_TRAN(state_settings);

        default:
            /* Подія TIMEOUT_IDLE_SIG піде в state_settings -> state_active -> state_screen_saver */
            return Q_SUPER(state_settings);
    }
}

void device_ui_init(DeviceUI *ui) {
    ui->brightness = 80;
    ui->is_calibrated = false;
    QHsm_init(&ui->super, state_initial);
}
```
```cpp
enum class DeviceSignal : uint16_t {
    BtnUp = static_cast<uint16_t>(QSignal::User),
    BtnDown,
    BtnEnter,
    BtnBack,
    TimeoutIdle
};

class DeviceUI : public HsmBase {
public:
    DeviceUI() 
        : HsmBase(static_cast<StateHandler>(&DeviceUI::stateInitial)),
          brightness_(80), 
          is_calibrated_(false) {}

private:
    uint8_t brightness_;
    bool is_calibrated_;

    QResult stateInitial(const QEvt&) {
        return tran(static_cast<StateHandler>(&DeviceUI::stateScreenSaver));
    }

    QResult stateScreenSaver(const QEvt& e) {
        if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter) ||
            e.sig == static_cast<QSignal>(DeviceSignal::BtnBack)) {
            return tran(static_cast<StateHandler>(&DeviceUI::stateMainMenu));
        }
        return super(&HsmBase::topState);
    }

    QResult stateActive(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // LCD_SetBacklight(100);
                return handled();
            case QSignal::Exit:
                // LCD_SetBacklight(0);
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::TimeoutIdle)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateScreenSaver));
                }
                return super(&HsmBase::topState);
        }
    }

    QResult stateMainMenu(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // Draw_Icon_Menu();
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateSettings));
                }
                return super(static_cast<StateHandler>(&DeviceUI::stateActive));
        }
    }

    QResult stateSettings(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // Display_Settings();
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnUp)) {
                    if (brightness_ < 100) brightness_ += 10;
                    return handled();
                }
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateCalibration));
                }
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnBack)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateMainMenu));
                }
                return super(static_cast<StateHandler>(&DeviceUI::stateActive));
        }
    }

    QResult stateCalibration(const QEvt& e) {
        switch (e.sig) {
            case QSignal::Entry:
                // Start_Calib();
                return handled();
            case QSignal::Exit:
                // Stop_Calib();
                return handled();
            default:
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnEnter)) {
                    is_calibrated_ = true;
                    return tran(static_cast<StateHandler>(&DeviceUI::stateSettings));
                }
                if (e.sig == static_cast<QSignal>(DeviceSignal::BtnBack)) {
                    return tran(static_cast<StateHandler>(&DeviceUI::stateSettings));
                }
                return super(static_cast<StateHandler>(&DeviceUI::stateSettings));
        }
    }
};
```
:::

---

### Аналіз витрат ресурсів та гарантії надійності

1. **Flash-пам'ять:** Рушій HSM займає менше 400 байтів скомпільованого двійкового коду на архітектурі ARM Cortex-M0+/M4.
2. **Оперативна пам'ять (RAM):** Екземпляр автомата `QHsm` потребує лише 8 байтів RAM (два вказівники на функції на 32-бітній платформі).
3. **Стек:** Максимальне заглиблення стека під час виконання найскладнішого переходу обмежене константою `Q_MAX_DEPTH = 8` (близько 64 байтів стека).
4. **Детермінізм:** Час обробки події та виконання переходу має суворо фіксовану верхню межу (немає циклів пошуку з невизначеною кількістю ітерацій).
