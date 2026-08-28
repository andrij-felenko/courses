#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Статуси оптичної лінії
typedef enum {
    LINK_STATUS_OK = 0,          // Запас лінії в межах норми (>= 3.0 дБ)
    LINK_STATUS_LOW_MARGIN,      // Сигнал доходить, але запас критичний (0 .. 3.0 дБ)
    LINK_STATUS_UNREACHABLE,     // Сигнал загашений нижче чутливості приймача
    LINK_STATUS_OVERLOADED       // Перевантаження приймача (ризик пошкодження діода)
} link_status_t;

// Параметри оптичного трансивера
typedef struct {
    float tx_power_dbm;          // Вихідна потужність передавача (дБм)
    float rx_sensitivity_dbm;    // Поріг чутливості приймача (дБм)
    float rx_overload_dbm;       // Рівень оптичного насичення (дБм)
} transceiver_spec_t;

// Параметри пасивної траси
typedef struct {
    float length_km;             // Довжина оптичного кабелю (км)
    float attenuation_per_km;    // Загасання волокна на робочій хвилі (дБ/км)
    int splice_count;            // Кількість зварних з'єднань
    float splice_loss_db;        // Втрати на одну зварку (дБ)
    int connector_count;         // Кількість з'єднувальних роз'ємів
    float connector_loss_db;     // Втрати на один роз'єм (дБ)
    int splitter_ratio;          // Коефіцієнт розщеплення сплітера (1, 2, 4, 8, 16, 32, 64)
    float splitter_excess_db;    // Додаткові втрати вставки сплітера (дБ)
    float system_margin_target;  // Нормативний інженерний запас (дБ, зазвичай 3.0)
} fiber_path_t;

// Результат розрахунку оптичного бюджету
typedef struct {
    float total_attenuation_db;  // Сумарне загасання тракту (дБ)
    float rx_power_dbm;          // Розрахункова потужність на приймачі (дБм)
    float margin_db;             // Фактичний залишковий запас (дБ)
    link_status_t status;        // Підсумковий статус лінії
} link_budget_result_t;

// Розрахунок втрат пасивного оптичного розгалужувача 1:N
static float calculate_splitter_loss(int ratio, float excess_loss_db) {
    if (ratio <= 1) return 0.0f;
    // Формула: 10 * log10(ratio) + excess_loss
    return 10.0f * log10f((float)ratio) + excess_loss_db;
}

// Головна функція розрахунку оптичного бюджету
link_budget_result_t calculate_link_budget(const transceiver_spec_t *tx_rx,
                                           const fiber_path_t *path) {
    link_budget_result_t result = {0};

    // 1. Загасання оптичного волокна
    float fiber_loss = path->length_km * path->attenuation_per_km;

    // 2. Втрати на зварювальних та рознімних з'єднаннях
    float splices_loss = (float)path->splice_count * path->splice_loss_db;
    float connectors_loss = (float)path->connector_count * path->connector_loss_db;

    // 3. Втрати на пасивному сплітері
    float splitter_loss = calculate_splitter_loss(path->splitter_ratio, path->splitter_excess_db);

    // 4. Сумарне загасання тракту
    result.total_attenuation_db = fiber_loss + splices_loss + connectors_loss + splitter_loss;

    // 5. Розрахункова потужність на фотодіоді приймача
    result.rx_power_dbm = tx_rx->tx_power_dbm - result.total_attenuation_db;

    // 6. Розрахунок запасу відносно чутливості
    result.margin_db = result.rx_power_dbm - tx_rx->rx_sensitivity_dbm;

    // 7. Оцінка стану лінії
    if (result.rx_power_dbm > tx_rx->rx_overload_dbm) {
        result.status = LINK_STATUS_OVERLOADED;
    } else if (result.rx_power_dbm < tx_rx->rx_sensitivity_dbm) {
        result.status = LINK_STATUS_UNREACHABLE;
    } else if (result.margin_db < path->system_margin_target) {
        result.status = LINK_STATUS_LOW_MARGIN;
    } else {
        result.status = LINK_STATUS_OK;
    }

    return result;
}

int main(void) {
    // Специфікація модуля GPON Class B+
    transceiver_spec_t gpon_b_plus = {
        .tx_power_dbm = 2.5f,          // +2.5 дБм (передавач OLT)
        .rx_sensitivity_dbm = -27.0f,  // -27.0 дБм (чутливість ONU)
        .rx_overload_dbm = -8.0f       // -8.0 дБм (перевантаження ONU)
    };

    // Параметри випробувальної траси GPON 12 км зі сплітером 1:32
    fiber_path_t path_12km = {
        .length_km = 12.0f,
        .attenuation_per_km = 0.35f,   // 1490 нм
        .splice_count = 5,
        .splice_loss_db = 0.04f,
        .connector_count = 4,
        .connector_loss_db = 0.25f,
        .splitter_ratio = 32,          // 1:32
        .splitter_excess_db = 1.8f,
        .system_margin_target = 3.0f
    };

    link_budget_result_t res = calculate_link_budget(&gpon_b_plus, &path_12km);

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ОПТИЧНОГО БЮДЖЕТУ ===\n");
    printf("Сумарне загасання тракту:  %.2f дБ\n", res.total_attenuation_db);
    printf("Потужність на приймачі:    %.2f дБм\n", res.rx_power_dbm);
    printf("Залишковий запас лінії:    %.2f дБ (норма >= %.1f дБ)\n",
           res.margin_db, path_12km.system_margin_target);

    switch (res.status) {
        case LINK_STATUS_OK:
            printf("СТАТУС: [ОК] Лінія надійна, запас достатній.\n");
            break;
        case LINK_STATUS_LOW_MARGIN:
            printf("СТАТУС: [УВАГА] Сигнал є, але запас нижчий за 3 дБ!\n");
            break;
        case LINK_STATUS_UNREACHABLE:
            printf("СТАТУС: [ПОМИЛКА] Зв'язок відсутній (загасання завелике).\n");
            break;
        case LINK_STATUS_OVERLOADED:
            printf("СТАТУС: [КРИТИЧНО] Засліплення приймача (потрібен атенюатор).\n");
            break;
    }

    return 0;
}
