# ⚙️ Польовий інтерфейс на базі LVGL: високий контраст, утримання кнопок та енкодер

Цей практичний модуль надає повну, оптимізовану для польових терміналів реалізацію людино-машинного інтерфейсу на базі вбудованої графічної бібліотеки LVGL (версій v8/v9). Тут розібрано архітектуру теми з динамічним перемиканням контрастних палітр, механізм створення захищеного від тремору віджета з утриманням (Hold-to-Confirm) та інтеграцію апаратного енкодера з груповою матрицею фокусування для керування в товстих тактичних рукавицях.

Без спеціалізованої адаптації стандартний фреймворк графічного інтерфейсу не здатний протистояти польовим факторам: яскравість прямого сонця вимиває напівпрозорі меню, вібрація техніки зриває одинарні кліки, а краплі дощу блокують сенсорну сітку. Нижче подано покроковий розбір кожної підсистеми з аналізом пасток пам'яті, потокобезпеки та крайових станів.

## 1. Архітектура польової теми: високий контраст та відмова від напівтонів

У звичайних інтерфейсах привабливість досягається за рахунок розмитих тіней, багатошарових градієнтів та тонких пастельних рамок товщиною 1 піксель. У польових умовах під освітленістю 100 000 лк усі ці елементи миттєво зливаються у нерозбірливу сіру масу. Ба більше, обчислення альфа-змішування (Alpha Blending) для напівпрозорих тіней навантажує мікроконтролер десятками тисяч зайвих операцій на кожен кадр, знижуючи частоту оновлення екрана.

Польова тема LVGL будується на трьох непорушних принципах:
1. **Повна непрозорість (`LV_OPA_COVER`)**: усі фонові шари, плашки та кнопки малюються зі 100% непрозорістю. Це дозволяє рушію рендерингу LVGL застосовувати швидке копіювання блоків пам'яті через DMA2D (Chrom-ART на STM32 або PPA на ESP32) без попіксельного програмного змішування.
2. **Товсті контрастні рамки (3–6 px)**: межа активного елемента повинна мати високу просторову частоту, щоб око миттєво фіксувало контур кнопки навіть під час бокового погляду через засмальцьоване скло.
3. **Фіксований тактильний розмір**: мінімальна ширина та висота інтерактивної зони примусово обмежуються значенням 95×95 пікселів (що на типових дисплеях 160 DPI відповідає фізичному розміру 15×15 мм).

> [!IMPORTANT]
> **Пастка пам'яті зі стилями LVGL**: структури `lv_style_t` у LVGL є дескрипторами властивостей. Вони **не копіюються** всередину віджета, а зберігаються за вказівником. Створення об'єкта `lv_style_t` як локальної змінної всередині функції або конструктора призводить до того, що після виходу зі стеку пам'ять перезаписується, викликаючи невизначену поведінку та падіння прошивки (HardFault). Усі стилі польової теми повинні бути або статичними (`static`), або членами довгоживучих класів-одинаків.

Розгляньмо повну реалізацію теми з двома палітрами (денна чорно-жовта та нічна темно-червона) мовами C та C++:

:::tabs
```c
#include "lvgl.h"
#include <stdbool.h>
#include <stdint.h>

/* Режими роботи польового інтерфейсу */
typedef enum {
    FIELD_MODE_DAY_HIGH_CONTRAST = 0,
    FIELD_MODE_NIGHT_RED
} field_color_mode_t;

typedef struct {
    lv_color_t bg;
    lv_color_t surface;
    lv_color_t text;
    lv_color_t border;
    lv_color_t accent;
    lv_color_t alert;
    lv_color_t safe;
} field_palette_t;

static const field_palette_t PALETTES[] = {
    [FIELD_MODE_DAY_HIGH_CONTRAST] = {
        .bg      = LV_COLOR_MAKE(0x00, 0x00, 0x00), // Чорний
        .surface = LV_COLOR_MAKE(0x1C, 0x1C, 0x1E), // Темно-сірий
        .text    = LV_COLOR_MAKE(0xFF, 0xFF, 0xFF), // Білий
        .border  = LV_COLOR_MAKE(0xFF, 0xFF, 0xFF), // Біла рамка
        .accent  = LV_COLOR_MAKE(0xFF, 0xD7, 0x00), // Золотаво-жовтий
        .alert   = LV_COLOR_MAKE(0xFF, 0x2D, 0x55), // Червоний
        .safe    = LV_COLOR_MAKE(0x34, 0xC7, 0x59)  // Зелений
    },
    [FIELD_MODE_NIGHT_RED] = {
        .bg      = LV_COLOR_MAKE(0x00, 0x00, 0x00), // Чорний
        .surface = LV_COLOR_MAKE(0x20, 0x00, 0x00), // Темно-червоний
        .text    = LV_COLOR_MAKE(0xFF, 0x3B, 0x30), // Насичений червоний
        .border  = LV_COLOR_MAKE(0x8B, 0x00, 0x00), // Бордовий
        .accent  = LV_COLOR_MAKE(0xFF, 0x45, 0x3A), // Світло-червоний
        .alert   = LV_COLOR_MAKE(0xFF, 0x00, 0x00), // Яскраво-червоний
        .safe    = LV_COLOR_MAKE(0x99, 0x1B, 0x1B)  // Приглушений червоний
    }
};

static field_color_mode_t current_mode = FIELD_MODE_DAY_HIGH_CONTRAST;
static lv_theme_t field_theme;
static lv_style_t style_btn_base;
static lv_style_t style_btn_focus;
static lv_style_t style_btn_press;
static lv_style_t style_scr;

static void field_theme_apply_cb(lv_theme_t *th, lv_obj_t *obj) {
    LV_UNUSED(th);
    if (lv_obj_check_type(obj, &lv_btn_class)) {
        lv_obj_add_style(obj, &style_btn_base, LV_STATE_DEFAULT);
        lv_obj_add_style(obj, &style_btn_focus, LV_STATE_FOCUSED);
        lv_obj_add_style(obj, &style_btn_press, LV_STATE_PRESSED);
    } else if (lv_obj_check_type(obj, &lv_screen_class) || lv_obj_get_parent(obj) == NULL) {
        lv_obj_add_style(obj, &style_scr, LV_STATE_DEFAULT);
    }
}

void field_theme_update_styles(field_color_mode_t mode) {
    current_mode = mode;
    const field_palette_t *p = &PALETTES[mode];

    /* Налаштування стилю головного екрана */
    lv_style_reset(&style_scr);
    lv_style_init(&style_scr);
    lv_style_set_bg_color(&style_scr, p->bg);
    lv_style_set_bg_opa(&style_scr, LV_OPA_COVER);

    /* Базовий стиль польової кнопки (15 мм) */
    lv_style_reset(&style_btn_base);
    lv_style_init(&style_btn_base);
    lv_style_set_min_width(&style_btn_base, 95);
    lv_style_set_min_height(&style_btn_base, 95);
    lv_style_set_bg_color(&style_btn_base, p->surface);
    lv_style_set_bg_opa(&style_btn_base, LV_OPA_COVER);
    lv_style_set_border_color(&style_btn_base, p->border);
    lv_style_set_border_width(&style_btn_base, 3);
    lv_style_set_radius(&style_btn_base, 8);
    lv_style_set_text_color(&style_btn_base, p->text);
    lv_style_set_pad_all(&style_btn_base, 14);

    /* Стиль фокусу енкодера / апаратних клавіш */
    lv_style_reset(&style_btn_focus);
    lv_style_init(&style_btn_focus);
    lv_style_set_border_color(&style_btn_focus, p->accent);
    lv_style_set_border_width(&style_btn_focus, 6);

    /* Стиль активного натискання */
    lv_style_reset(&style_btn_press);
    lv_style_init(&style_btn_press);
    lv_style_set_bg_color(&style_btn_press, p->accent);
    lv_style_set_text_color(&style_btn_press, p->bg);
}

void field_theme_init(lv_display_t *disp, field_color_mode_t initial_mode) {
    field_theme_update_styles(initial_mode);
    lv_theme_set_apply_cb(&field_theme, field_theme_apply_cb);
    lv_theme_set_display(&field_theme, disp);
    lv_display_set_theme(disp, &field_theme);
}
```
```cpp
#include "lvgl.h"
#include <cstdint>
#include <array>
#include <memory>

namespace field_ui {

enum class ColorMode : uint8_t {
    DayHighContrast = 0,
    NightRed
};

struct Palette {
    lv_color_t background;
    lv_color_t surface;
    lv_color_t text;
    lv_color_t border;
    lv_color_t accent;
    lv_color_t alert;
    lv_color_t safe;
};

class FieldTheme {
public:
    static FieldTheme& instance() {
        static FieldTheme theme;
        return theme;
    }

    void setup(lv_display_t* disp, ColorMode mode = ColorMode::DayHighContrast) {
        display_ = disp;
        setMode(mode);

        lv_theme_set_apply_cb(&theme_, &FieldTheme::applyCallbackThunk);
        lv_theme_set_display(&theme_, disp);
        lv_display_set_theme(disp, &theme_);
    }

    void setMode(ColorMode mode) {
        current_mode_ = mode;
        const auto& p = palettes_[static_cast<size_t>(mode)];

        lv_style_reset(&style_screen_);
        lv_style_init(&style_screen_);
        lv_style_set_bg_color(&style_screen_, p.background);
        lv_style_set_bg_opa(&style_screen_, LV_OPA_COVER);

        lv_style_reset(&style_btn_base_);
        lv_style_init(&style_btn_base_);
        lv_style_set_min_width(&style_btn_base_, 95);
        lv_style_set_min_height(&style_btn_base_, 95);
        lv_style_set_bg_color(&style_btn_base_, p.surface);
        lv_style_set_bg_opa(&style_btn_base_, LV_OPA_COVER);
        lv_style_set_border_color(&style_btn_base_, p.border);
        lv_style_set_border_width(&style_btn_base_, 3);
        lv_style_set_radius(&style_btn_base_, 8);
        lv_style_set_text_color(&style_btn_base_, p.text);
        lv_style_set_pad_all(&style_btn_base_, 14);

        lv_style_reset(&style_btn_focus_);
        lv_style_init(&style_btn_focus_);
        lv_style_set_border_color(&style_btn_focus_, p.accent);
        lv_style_set_border_width(&style_btn_focus_, 6);

        lv_style_reset(&style_btn_press_);
        lv_style_init(&style_btn_press_);
        lv_style_set_bg_color(&style_btn_press_, p.accent);
        lv_style_set_text_color(&style_btn_press_, p.background);

        if (display_) {
            lv_obj_report_style_change(&style_screen_);
            lv_obj_report_style_change(&style_btn_base_);
        }
    }

    [[nodiscard]] const Palette& currentPalette() const noexcept {
        return palettes_[static_cast<size_t>(current_mode_)];
    }

private:
    FieldTheme() = default;

    static void applyCallbackThunk(lv_theme_t* th, lv_obj_t* obj) {
        auto& self = instance();
        if (lv_obj_check_type(obj, &lv_btn_class)) {
            lv_obj_add_style(obj, &self.style_btn_base_, LV_STATE_DEFAULT);
            lv_obj_add_style(obj, &self.style_btn_focus_, LV_STATE_FOCUSED);
            lv_obj_add_style(obj, &self.style_btn_press_, LV_STATE_PRESSED);
        } else if (lv_obj_check_type(obj, &lv_screen_class) || lv_obj_get_parent(obj) == nullptr) {
            lv_obj_add_style(obj, &self.style_screen_, LV_STATE_DEFAULT);
        }
    }

    lv_display_t* display_{nullptr};
    ColorMode current_mode_{ColorMode::DayHighContrast};
    lv_theme_t theme_{};

    lv_style_t style_screen_{};
    lv_style_t style_btn_base_{};
    lv_style_t style_btn_focus_{};
    lv_style_t style_btn_press_{};

    static constexpr std::array<Palette, 2> palettes_{{
        // Day High Contrast
        Palette{
            .background = { .blue = 0x00, .green = 0x00, .red = 0x00 },
            .surface    = { .blue = 0x1E, .green = 0x1C, .red = 0x1C },
            .text       = { .blue = 0xFF, .green = 0xFF, .red = 0xFF },
            .border     = { .blue = 0xFF, .green = 0xFF, .red = 0xFF },
            .accent     = { .blue = 0x00, .green = 0xD7, .red = 0xFF },
            .alert      = { .blue = 0x55, .green = 0x2D, .red = 0xFF },
            .safe       = { .blue = 0x59, .green = 0xC7, .red = 0x34 }
        },
        // Night Red
        Palette{
            .background = { .blue = 0x00, .green = 0x00, .red = 0x00 },
            .surface    = { .blue = 0x00, .green = 0x00, .red = 0x20 },
            .text       = { .blue = 0x30, .green = 0x3B, .red = 0xFF },
            .border     = { .blue = 0x00, .green = 0x00, .red = 0x8B },
            .accent     = { .blue = 0x3A, .green = 0x45, .red = 0xFF },
            .alert      = { .blue = 0x00, .green = 0x00, .red = 0xFF },
            .safe       = { .blue = 0x1B, .green = 0x1B, .red = 0x99 }
        }
    }};
};

} // namespace field_ui
```
:::

---

## 2. Віджет захищеного утримання: анатомія подій та крайові стани

Традиційні графічні кнопки генерують подію спрацьовування за подією `LV_EVENT_CLICKED`, тобто у момент відпускання пальця після натискання. У рухомому транспортному засобі під час поштовху на ямі рука оператора короткочасно б'є по сенсорному склу — виникає серія імпульсів «натиснув–відпустив» тривалістю 50–120 мс. Якщо в зоні удару опинилася кнопка «Disarm» або «Motor Cutoff», безпілотник зазнає аварії.

Віджет `TacticalHoldButton` реалізує строгий скінченний автомат накопичення часу утримання.

### Послідовність станів та обробка зриву пальця

1. **Початок дотику (`LV_EVENT_PRESSED`)**:
   - Таймер скидається в `elapsed_ms = 0`.
   - Кругова дуга `lv_arc` переводиться у нульове положення.
   - Запускається періодичний таймер LVGL із кроком 30 мс (`lv_timer_resume`).
2. **Процес утримання (Timer Ticks)**:
   - Кожні 30 мс значення накопиченого часу збільшується.
   - Обчислюється прогрес від 0 до 100 %, і дуга оновлює свій кут повороту навколо напису кнопки.
   - Якщо `elapsed_ms >= hold_time_ms`, таймер зупиняється, скидається дуга і викликається функція зворотного виклику підтвердження (`confirm_cb`).
3. **Швидке відпускання або зісковзування (`LV_EVENT_RELEASED` / `LV_EVENT_PRESS_LOST`)**:
   - Якщо оператор прибрав палець раніше досягнення повної тривалості (наприклад, через 600 мс), або якщо під час вібрації палець зісковзнув за межі активної області кнопки (`LV_EVENT_PRESS_LOST`), таймер **негайно зупиняється**, а прогрес дуги миттєво обнуляється.

:::tabs
```c
#include "lvgl.h"
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    lv_obj_t *btn;
    lv_obj_t *arc;
    lv_obj_t *label;
    lv_timer_t *timer;
    uint32_t hold_time_ms;
    uint32_t elapsed_ms;
    void (*on_confirm)(void *user_data);
    void *user_data;
} tactical_hold_btn_t;

static void hold_timer_cb(lv_timer_t *t) {
    tactical_hold_btn_t *hb = (tactical_hold_btn_t *)lv_timer_get_user_data(t);
    hb->elapsed_ms += 30;

    int32_t progress = (int32_t)((hb->elapsed_ms * 100) / hb->hold_time_ms);
    if (progress > 100) progress = 100;
    lv_arc_set_value(hb->arc, progress);

    if (hb->elapsed_ms >= hb->hold_time_ms) {
        lv_timer_pause(t);
        hb->elapsed_ms = 0;
        lv_arc_set_value(hb->arc, 0);
        if (hb->on_confirm) {
            hb->on_confirm(hb->user_data);
        }
    }
}

static void hold_event_cb(lv_event_t *e) {
    tactical_hold_btn_t *hb = (tactical_hold_btn_t *)lv_event_get_user_data(e);
    lv_event_code_t code = lv_event_get_code(e);

    if (code == LV_EVENT_PRESSED) {
        hb->elapsed_ms = 0;
        lv_arc_set_value(hb->arc, 0);
        lv_timer_resume(hb->timer);
    } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
        lv_timer_pause(hb->timer);
        hb->elapsed_ms = 0;
        lv_arc_set_value(hb->arc, 0);
    }
}

tactical_hold_btn_t* tactical_hold_btn_create(lv_obj_t *parent, const char *text, 
                                             uint32_t hold_ms, 
                                             void (*confirm_cb)(void *), void *user_data) {
    tactical_hold_btn_t *hb = (tactical_hold_btn_t *)lv_malloc(sizeof(tactical_hold_btn_t));
    if (!hb) return NULL;

    hb->hold_time_ms = hold_ms;
    hb->elapsed_ms   = 0;
    hb->on_confirm   = confirm_cb;
    hb->user_data    = user_data;

    hb->btn = lv_btn_create(parent);
    lv_obj_set_size(hb->btn, 110, 110);

    hb->label = lv_label_create(hb->btn);
    lv_label_set_text(hb->label, text);
    lv_obj_center(hb->label);

    hb->arc = lv_arc_create(hb->btn);
    lv_obj_set_size(hb->arc, 100, 100);
    lv_arc_set_rotation(hb->arc, 270);
    lv_arc_set_bg_angles(hb->arc, 0, 360);
    lv_arc_set_angles(hb->arc, 0, 0);
    lv_arc_set_range(hb->arc, 0, 100);
    lv_obj_set_style_arc_width(hb->arc, 5, LV_PART_INDICATOR);
    lv_obj_remove_style(hb->arc, NULL, LV_PART_KNOB);
    lv_obj_clear_flag(hb->arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_center(hb->arc);

    hb->timer = lv_timer_create(hold_timer_cb, 30, hb);
    lv_timer_pause(hb->timer);

    lv_obj_add_event_cb(hb->btn, hold_event_cb, LV_EVENT_ALL, hb);
    return hb;
}
```
```cpp
#include "lvgl.h"
#include <functional>
#include <memory>
#include <string_view>

namespace field_ui {

class TacticalHoldButton {
public:
    using Callback = std::function<void()>;

    TacticalHoldButton(lv_obj_t* parent, std::string_view label, uint32_t hold_time_ms, Callback cb)
        : hold_time_ms_(hold_time_ms), callback_(std::move(cb)) {

        btn_ = lv_btn_create(parent);
        lv_obj_set_size(btn_, 110, 110);

        label_ = lv_label_create(btn_);
        lv_label_set_text(label_, label.data());
        lv_obj_center(label_);

        arc_ = lv_arc_create(btn_);
        lv_obj_set_size(arc_, 100, 100);
        lv_arc_set_rotation(arc_, 270);
        lv_arc_set_bg_angles(arc_, 0, 360);
        lv_arc_set_angles(arc_, 0, 0);
        lv_arc_set_range(arc_, 0, 100);
        lv_obj_set_style_arc_width(arc_, 5, LV_PART_INDICATOR);
        lv_obj_remove_style(arc_, nullptr, LV_PART_KNOB);
        lv_obj_clear_flag(arc_, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_center(arc_);

        timer_ = lv_timer_create(&TacticalHoldButton::onTimerThunk, 30, this);
        lv_timer_pause(timer_);

        lv_obj_add_event_cb(btn_, &TacticalHoldButton::onEventThunk, LV_EVENT_ALL, this);
    }

    ~TacticalHoldButton() {
        if (timer_) {
            lv_timer_delete(timer_);
            timer_ = nullptr;
        }
    }

    TacticalHoldButton(const TacticalHoldButton&) = delete;
    TacticalHoldButton& operator=(const TacticalHoldButton&) = delete;

    [[nodiscard]] lv_obj_t* handle() const noexcept { return btn_; }

private:
    static void onTimerThunk(lv_timer_t* t) {
        auto* self = static_cast<TacticalHoldButton*>(lv_timer_get_user_data(t));
        self->handleTick();
    }

    static void onEventThunk(lv_event_t* e) {
        auto* self = static_cast<TacticalHoldButton*>(lv_event_get_user_data(e));
        self->handleEvent(lv_event_get_code(e));
    }

    void handleTick() {
        elapsed_ms_ += 30;
        int32_t progress = static_cast<int32_t>((elapsed_ms_ * 100) / hold_time_ms_);
        if (progress > 100) progress = 100;
        lv_arc_set_value(arc_, progress);

        if (elapsed_ms_ >= hold_time_ms_) {
            lv_timer_pause(timer_);
            elapsed_ms_ = 0;
            lv_arc_set_value(arc_, 0);
            if (callback_) {
                callback_();
            }
        }
    }

    void handleEvent(lv_event_code_t code) {
        if (code == LV_EVENT_PRESSED) {
            elapsed_ms_ = 0;
            lv_arc_set_value(arc_, 0);
            lv_timer_resume(timer_);
        } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
            lv_timer_pause(timer_);
            elapsed_ms_ = 0;
            lv_arc_set_value(arc_, 0);
        }
    }

    uint32_t hold_time_ms_{1500};
    uint32_t elapsed_ms_{0};
    Callback callback_;
    lv_obj_t* btn_{nullptr};
    lv_obj_t* label_{nullptr};
    lv_obj_t* arc_{nullptr};
    lv_timer_t* timer_{nullptr};
};

} // namespace field_ui
```
:::

---

## 3. Апаратна інтеграція енкодера: групи навігації та потокобезпека

Для повної відмови від сенсорного скла під час зливи екранні віджети об'єднуються в навігаційну групу `lv_group_t`. Інкрементальний оптичний або магнітний енкодер генерує імпульси при обертанні вала.

### Потокобезпека між ISR та LVGL

Імпульси від енкодера зчитуються в апаратному таймері або в обробнику переривань GPIO (ISR) з частотою до кількох кілогерців. Безпосередній виклик функцій LVGL зсередини переривання **суворо заборонений**, оскільки структури LVGL не є потокобезпечними.

Правильний патерн:
- Обробник переривання лише оновлює атомарний лічильник накопичених кроків (`atomic int16_t encoder_counter`).
- Драйвер LVGL (`encoder_read_cb`) викликається з головного циклу `lv_timer_handler()` раз на 10–20 мс, забирає накопичену різницю кроків і скидає лічильник на нуль.

:::tabs
```c
#include "lvgl.h"
#include <stdint.h>
#include <stdbool.h>

/* Зовнішні апаратні функції, що працюють з атомарними змінними переривань */
extern int16_t hardware_encoder_get_and_clear_diff(void);
extern bool    hardware_encoder_is_button_down(void);

static lv_indev_t *encoder_indev = NULL;
static lv_group_t *field_nav_group = NULL;

static void encoder_read_cb(lv_indev_t *indev, lv_indev_data_t *data) {
    LV_UNUSED(indev);

    /* Зчитуємо кроки, накопичені з моменту останнього виклику */
    data->enc_diff = hardware_encoder_get_and_clear_diff();

    /* Стан кнопки підтвердження енкодера */
    if (hardware_encoder_is_button_down()) {
        data->state = LV_INDEV_STATE_PRESSED;
    } else {
        data->state = LV_INDEV_STATE_RELEASED;
    }
}

void field_input_init(void) {
    field_nav_group = lv_group_create();
    lv_group_set_default(field_nav_group);

    encoder_indev = lv_indev_create();
    lv_indev_set_type(encoder_indev, LV_INDEV_TYPE_ENCODER);
    lv_indev_set_read_cb(encoder_indev, encoder_read_cb);
    lv_indev_set_group(encoder_indev, field_nav_group);
}

void field_input_add_widget(lv_obj_t *obj) {
    if (field_nav_group && obj) {
        lv_group_add_obj(field_nav_group, obj);
    }
}
```
```cpp
#include "lvgl.h"
#include <span>
#include <cstdint>

namespace field_ui {

class HardwareEncoderDriver {
public:
    using DiffReader = int16_t(*)();
    using ButtonReader = bool(*)();

    static HardwareEncoderDriver& instance() {
        static HardwareEncoderDriver driver;
        return driver;
    }

    void initialize(DiffReader diff_fn, ButtonReader btn_fn) {
        diff_reader_ = diff_fn;
        btn_reader_  = btn_fn;

        group_ = lv_group_create();
        lv_group_set_default(group_);

        indev_ = lv_indev_create();
        lv_indev_set_type(indev_, LV_INDEV_TYPE_ENCODER);
        lv_indev_set_read_cb(indev_, &HardwareEncoderDriver::readCallbackThunk);
        lv_indev_set_group(indev_, group_);
        lv_indev_set_user_data(indev_, this);
    }

    void registerWidget(lv_obj_t* obj) {
        if (group_ && obj) {
            lv_group_add_obj(group_, obj);
        }
    }

    void registerWidgets(std::span<lv_obj_t*> widgets) {
        for (auto* obj : widgets) {
            registerWidget(obj);
        }
    }

    [[nodiscard]] lv_group_t* group() const noexcept { return group_; }

private:
    HardwareEncoderDriver() = default;

    static void readCallbackThunk(lv_indev_t* indev, lv_indev_data_t* data) {
        auto* self = static_cast<HardwareEncoderDriver*>(lv_indev_get_user_data(indev));
        if (self) {
            self->handleRead(data);
        }
    }

    void handleRead(lv_indev_data_t* data) {
        data->enc_diff = diff_reader_ ? diff_reader_() : 0;
        data->state    = (btn_reader_ && btn_reader_()) 
                         ? LV_INDEV_STATE_PRESSED 
                         : LV_INDEV_STATE_RELEASED;
    }

    DiffReader diff_reader_{nullptr};
    ButtonReader btn_reader_{nullptr};
    lv_indev_t* indev_{nullptr};
    lv_group_t* group_{nullptr};
};

} // namespace field_ui
```
:::

---

## 4. Збірка завершеного польового екрана (Field Dashboard Layout)

Нижче наведено код збірки повнофункціонального екрана оператора: верхній статус-бар для статичної телеметрії, центральна зона під огляд карти та нижній блок керування для великого пальця з кнопками розміром 110×110 px і захисними проміжками 25 px.

:::tabs
```c
#include "lvgl.h"

static void on_arm_confirmed(void *user_data) {
    LV_UNUSED(user_data);
    /* Виклик протоколу MAVLink / команди на борт */
}

static void on_mode_toggle(lv_event_t *e) {
    if (lv_event_get_code(e) == LV_EVENT_CLICKED) {
        /* Перемикання польотного режиму */
    }
}

void build_field_ui_screen(lv_display_t *disp) {
    field_theme_init(disp, FIELD_MODE_DAY_HIGH_CONTRAST);
    field_input_init();

    lv_obj_t *scr = lv_screen_active();
    lv_obj_set_flex_flow(scr, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(scr, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    /* 1. Верхня зона (Hard-to-Reach): статичні показники */
    lv_obj_t *top_bar = lv_obj_create(scr);
    lv_obj_set_size(top_bar, LV_PCT(100), 40);
    lv_obj_set_style_bg_color(top_bar, lv_color_hex(0x000000), 0);
    lv_obj_set_style_border_width(top_bar, 0, 0);

    lv_obj_t *telemetry_lbl = lv_label_create(top_bar);
    lv_label_set_text(telemetry_lbl, "BAT: 24.8V | GPS: 18 FIX | ALT: 120m | RSSI: -68dBm");
    lv_obj_center(telemetry_lbl);

    /* 2. Середня зона (Stretch Zone): карта / журнал */
    lv_obj_t *mid_panel = lv_obj_create(scr);
    lv_obj_set_size(mid_panel, LV_PCT(100), 260);

    /* 3. Нижня зона великого пальця (Natural Thumb Zone): кнопки 17 мм із зазором 25 px */
    lv_obj_t *bottom_bar = lv_obj_create(scr);
    lv_obj_set_size(bottom_bar, LV_PCT(100), 140);
    lv_obj_set_flex_flow(bottom_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(bottom_bar, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_gap(bottom_bar, 25, 0);

    /* Звичайна тактильна кнопка зміни режиму */
    lv_obj_t *btn_mode = lv_btn_create(bottom_bar);
    lv_obj_set_size(btn_mode, 110, 110);
    lv_obj_t *lbl_mode = lv_label_create(btn_mode);
    lv_label_set_text(lbl_mode, "MODE\nAUTO");
    lv_obj_center(lbl_mode);
    lv_obj_add_event_cb(btn_mode, on_mode_toggle, LV_EVENT_CLICKED, NULL);
    field_input_add_widget(btn_mode);

    /* Критична кнопка активації з утриманням 1.5 с */
    tactical_hold_btn_t *arm_btn = tactical_hold_btn_create(bottom_bar, "ARM\nHOLD 1.5s", 1500, on_arm_confirmed, NULL);
    field_input_add_widget(arm_btn->btn);
}
```
```cpp
#include "lvgl.h"
#include <memory>
#include <vector>

namespace field_ui {

class FieldDashboard {
public:
    explicit FieldDashboard(lv_display_t* disp) {
        FieldTheme::instance().setup(disp, ColorMode::DayHighContrast);

        auto* scr = lv_screen_active();
        lv_obj_set_flex_flow(scr, LV_FLEX_FLOW_COLUMN);
        lv_obj_set_flex_align(scr, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

        // 1. Верхня статична зона
        top_bar_ = lv_obj_create(scr);
        lv_obj_set_size(top_bar_, LV_PCT(100), 40);
        lv_obj_set_style_bg_color(top_bar_, lv_color_hex(0x000000), 0);
        lv_obj_set_style_border_width(top_bar_, 0, 0);

        telemetry_label_ = lv_label_create(top_bar_);
        lv_label_set_text(telemetry_label_, "BAT: 24.8V | GPS: 18 FIX | ALT: 120m | RSSI: -68dBm");
        lv_obj_center(telemetry_label_);

        // 2. Середня зона
        middle_view_ = lv_obj_create(scr);
        lv_obj_set_size(middle_view_, LV_PCT(100), 260);

        // 3. Нижня зона великого пальця
        bottom_bar_ = lv_obj_create(scr);
        lv_obj_set_size(bottom_bar_, LV_PCT(100), 140);
        lv_obj_set_flex_flow(bottom_bar_, LV_FLEX_FLOW_ROW);
        lv_obj_set_flex_align(bottom_bar_, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
        lv_obj_set_style_pad_gap(bottom_bar_, 25, 0);

        // Кнопка режиму
        mode_btn_ = lv_btn_create(bottom_bar_);
        lv_obj_set_size(mode_btn_, 110, 110);
        auto* mode_lbl = lv_label_create(mode_btn_);
        lv_label_set_text(mode_lbl, "MODE\nAUTO");
        lv_obj_center(mode_lbl);
        HardwareEncoderDriver::instance().registerWidget(mode_btn_);

        // Кнопка Arm з утриманням 1.5 с
        arm_button_ = std::make_unique<TacticalHoldButton>(
            bottom_bar_,
            "ARM\nHOLD 1.5s",
            1500,
            [this]() { onArmTriggered(); }
        );
        HardwareEncoderDriver::instance().registerWidget(arm_button_->handle());
    }

private:
    void onArmTriggered() {
        // Відправка критичної команди на виконавчий механізм
    }

    lv_obj_t* top_bar_{nullptr};
    lv_obj_t* telemetry_label_{nullptr};
    lv_obj_t* middle_view_{nullptr};
    lv_obj_t* bottom_bar_{nullptr};
    lv_obj_t* mode_btn_{nullptr};
    std::unique_ptr<TacticalHoldButton> arm_button_;
};

} // namespace field_ui
```
:::
