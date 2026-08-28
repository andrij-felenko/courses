#include <stdint.h>
#include <stdbool.h>

// ── Пороги (у відліках АЦП 12 біт, опорна 3.3 В, дільник вузла 1:11) ──
// Вузол стоку через дільник 10:1 заходить в ADC: V_adc = V_node / 11.
#define ADC_NODE_LOW     400     // < цього — вузол «низький» (притиснутий до землі)
#define ADC_NODE_HIGH    2200    // > цього — вузол «високий» (≈ +V або кламп)

// ── Дедлайни (мс), задаються під конкретне навантаження ──
#define T_TURNON_SETTLE  2       // скільки чекати, поки вузол сяде після ввімкнення
#define T_CLAMP_MAX      8       // максимально допустима тривалість полиці клампа
#define T_OFF_SETTLE     2       // скільки чекати усталення після вимкнення

typedef enum {
    SW_IDLE = 0,   // ключ закритий, спокій
    SW_TURN_ON,    // дали ON, чекаємо, що вузол сяде до землі
    SW_ON,         // усталене проведення
    SW_TURN_OFF,   // фаза гасіння — кламп тримає полицю
    SW_FAULT       // зафіксована аварія, ключ примусово закритий
} sw_state_t;

typedef enum {
    FAULT_NONE = 0,
    FAULT_OPEN_COIL,    // ввімкнули, а вузол не сів — обрив/нема навантаження
    FAULT_SHORT_SW,     // вимкнули, а вузол лишився низьким — ключ коротить
    FAULT_CLAMP_TIMEOUT // полиця клампа триває довше норми — застрягання/L більша
} fault_t;

typedef struct {
    sw_state_t state;
    fault_t    fault;
    uint32_t   t_state;     // мітка часу входу в поточний стан (мс)
    uint16_t   adc_node;    // остання вибірка вузла
    edge_mode_t edge;       // яка передача фронту вимкнення
} sw_ctx_t;

static sw_ctx_t sw;

// ── Зовнішні залежності (реалізує платформа) ──
extern uint32_t now_ms(void);            // монотонний час, мс
extern uint16_t adc_read_node(void);     // миттєва вибірка вузла стоку
extern void     gate_on(void);
extern void     gate_off(edge_mode_t m);

static void enter(sw_state_t s) { sw.state = s; sw.t_state = now_ms(); }

static void trip(fault_t f) {        // зафіксувати аварію — ключ геть
    gate_off(EDGE_FAST);             // в аварії гасимо різко: головне — закрити
    sw.fault = f;
    enter(SW_FAULT);
}

// Команди зовні
void sw_request_on(void)  { if (sw.state == SW_IDLE) enter(SW_TURN_ON), gate_on(); }
void sw_request_off(void) { if (sw.state == SW_ON)   enter(SW_TURN_OFF), gate_off(sw.edge); }

void sw_fault_clear(void) {          // ЯВНЕ скидання зі старшого рівня
    if (sw.state == SW_FAULT) { sw.fault = FAULT_NONE; enter(SW_IDLE); }
}

void sw_init(edge_mode_t edge) {
    sw.edge = edge; sw.fault = FAULT_NONE; gate_off(EDGE_FAST); enter(SW_IDLE);
}

// ── Серце: викликати періодично (напр., раз на 1 мс із таймера) ──
void sw_poll(void) {
    uint32_t dt = now_ms() - sw.t_state;
    sw.adc_node = adc_read_node();        // вибірка вузла В ПОТРІБНОМУ вікні

    switch (sw.state) {
    case SW_TURN_ON:
        // Вікно: після ввімкнення вузол МУСИТЬ сісти до землі.
        if (sw.adc_node < ADC_NODE_LOW) {
            enter(SW_ON);                 // навантаження озвалося — все добре
        } else if (dt >= T_TURNON_SETTLE) {
            trip(FAULT_OPEN_COIL);        // не сів за дедлайн → обрив котушки
        }
        break;

    case SW_ON:
        // У проведенні вузол має лишатися низьким. Підскочив — щось не так.
        if (sw.adc_node > ADC_NODE_HIGH) {
            trip(FAULT_OPEN_COIL);        // навантаження зникло на ходу
        }
        break;

    case SW_TURN_OFF:
        // Вікно: вузол злетів на полицю клампа й має сісти назад до +V.
        // «Сісти» = опуститися нижче ADC_NODE_HIGH (полиця скінчилася).
        if (sw.adc_node < ADC_NODE_HIGH) {
            // полиця завершилась — перевіримо, що ключ закрився, а не коротить
            if (sw.adc_node < ADC_NODE_LOW) {
                trip(FAULT_SHORT_SW);     // вузол притиснутий до землі — ключ коротить
            } else {
                enter(SW_IDLE);           // штатно вимкнулися
            }
        } else if (dt >= T_CLAMP_MAX) {
            trip(FAULT_CLAMP_TIMEOUT);    // полиця тягнеться задовго → застрягання
        }
        break;

    case SW_FAULT:
        gate_off(EDGE_FAST);              // тримаємо ключ закритим, чекаємо clear
        break;

    case SW_IDLE:
    default:
        break;
    }
}
