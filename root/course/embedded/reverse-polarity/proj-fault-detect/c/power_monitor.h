// power_monitor.h — монітор захищеної шини живлення:
//   вимір напруги дільником+АЦП, гістерезис, класифікація аварії, реакція.
//   Голе залізо: без malloc, фіксований розмір, без блокувань.
#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include <stdint.h>
#include <stdbool.h>

// Клас стану входу живлення — саме те, заради чого монітор існує.
typedef enum {
    PM_OK = 0,        // шина в нормі, живлення дійшло
    PM_SAG,           // просад: живлення є, але нижче норми (слабке джерело/кабель)
    PM_DEAD,          // мертва шина: ≈0 В (обрив або згорілий запобіжник)
    PM_BODYDIODE      // струм крізь body-діод: FET недовідкрився (реверс/низький Vin)
} pm_class_t;

// Незмінна конфігурація — заповнюється раз під конкретну плату.
typedef struct {
    uint16_t div_num, div_den;   // коефіцієнт дільника: Vшини = Vадц * num/den
    uint16_t vref_mv;            // опора АЦП у мВ (повна шкала)
    uint16_t adc_full;           // максимальний код АЦП (напр. 4095 для 12 біт)

    uint16_t v_nominal_mv;       // очікувана напруга шини в нормі, мВ
    uint16_t v_dead_mv;          // нижче цього шина вважається мертвою
    uint16_t v_sag_trip_mv;      // нижче цього — просад (спрацювання)
    uint16_t v_sag_heal_mv;      // вище цього — просад знято (відпускання) > trip
    uint16_t diode_drop_mv;      // падіння body-діода (для розпізнавання, ~600 мВ)
    uint16_t diode_tol_mv;       // допуск навколо «Vвх − diode_drop»

    uint8_t  confirm_dead;       // скільки поганих поспіль → PM_DEAD (мало)
    uint8_t  confirm_sag;        // скільки поганих поспіль → PM_SAG (більше)
    uint8_t  confirm_ok;         // скільки добрих поспіль → назад у PM_OK (велике)
} pm_config_t;

// Робочий стан — нуль на старті означає «холодний, ще не міряли».
typedef struct {
    const pm_config_t *cfg;
    pm_class_t st;               // поточний клас
    uint16_t   bus_mv;           // останнє усереднене значення шини, мВ
    uint32_t   sum;              // біжуча сума кільцевого буфера
    uint16_t   buf[8];           // кільцевий буфер відліків (сирий код АЦП)
    uint8_t    head, count;      // курсор і наповнення буфера
    uint8_t    bad_run, good_run;// поганих / добрих поспіль (для гістерезису)
    bool       flag_latched;     // «була аварія» — липкий прапорець для сервісу
} pm_channel_t;

// Функція вимірювання — даємо монітору спосіб прочитати сирий код АЦП шини.
// Так модуль не прив'язаний до конкретного АЦП (STM32, ESP32, будь-що).
typedef uint16_t (*pm_read_adc_t)(void);

// Реакції-callback: монітор кличе їх у МОМЕНТ переходу, з контексту poll().
typedef struct {
    void (*save_state)(void);            // зберегти критичне у NVM
    void (*set_load)(bool on);           // зняти/подати навантаження (ключ)
    void (*on_class)(pm_class_t cls);    // повідомити про новий клас (індикація/лог)
} pm_actions_t;

void       pm_init(pm_channel_t *ch, const pm_config_t *cfg);
void       pm_poll(pm_channel_t *ch, pm_read_adc_t read, const pm_actions_t *act);
pm_class_t pm_class(const pm_channel_t *ch);   // поточний клас
uint16_t   pm_bus_mv(const pm_channel_t *ch);  // остання напруга шини, мВ
bool       pm_fault_latched(const pm_channel_t *ch); // чи була аварія від старту

#endif
