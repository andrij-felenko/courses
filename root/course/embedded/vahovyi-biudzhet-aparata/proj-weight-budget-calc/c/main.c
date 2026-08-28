#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_COMPONENTS 32
#define GRAVITY_MSS 9.80665f

typedef enum {
    CAT_PAYLOAD = 0,
    CAT_BATTERY,
    CAT_PROPULSION,
    CAT_AVIONICS,
    CAT_AIRFRAME,
    CAT_MARGIN,
    CAT_COUNT
} ComponentCategory;

static const char* const CATEGORY_NAMES[] = {
    "Корисне навантаження",
    "Акумуляторна батарея",
    "Силова установка",
    "Бортова авіоніка",
    "Планер і кріплення",
    "Конструкторський резерв"
};

typedef struct {
    char name[40];
    ComponentCategory category;
    float mass_g;
    float x_mm;
    float y_mm;
    float z_mm;
    float power_w;
} Component;

typedef struct {
    Component items[MAX_COMPONENTS];
    size_t count;
    int motor_count;
    float max_thrust_per_motor_g;
    float cot_x_mm;
    float cot_y_mm;
} WeightBudget;

typedef struct {
    float mtow_g;
    float category_mass_g[CAT_COUNT];
    float category_fraction[CAT_COUNT];
    float cg_x_mm;
    float cg_y_mm;
    float cg_z_mm;
    float cg_offset_mm;
    float twr;
    float total_idle_power_w;
    bool is_balanced;
    bool is_twr_sufficient;
    bool is_battery_fraction_ok;
} BudgetAnalysis;

void budget_init(WeightBudget* budget, int motor_count, float max_thrust_g, float cot_x, float cot_y) {
    budget->count = 0;
    budget->motor_count = motor_count;
    budget->max_thrust_per_motor_g = max_thrust_g;
    budget->cot_x_mm = cot_x;
    budget->cot_y_mm = cot_y;
    memset(budget->items, 0, sizeof(budget->items));
}

bool budget_add(WeightBudget* budget, const char* name, ComponentCategory cat, 
                float mass_g, float x, float y, float z, float power_w) {
    if (budget->count >= MAX_COMPONENTS) {
        return false;
    }
    Component* item = &budget->items[budget->count++];
    strncpy(item->name, name, sizeof(item->name) - 1);
    item->name[sizeof(item->name) - 1] = '\0';
    item->category = cat;
    item->mass_g = mass_g;
    item->x_mm = x;
    item->y_mm = y;
    item->z_mm = z;
    item->power_w = power_w;
    return true;
}

BudgetAnalysis budget_calculate(const WeightBudget* budget) {
    BudgetAnalysis res;
    memset(&res, 0, sizeof(res));

    float sum_mx = 0.0f;
    float sum_my = 0.0f;
    float sum_mz = 0.0f;

    for (size_t i = 0; i < budget->count; ++i) {
        const Component* it = &budget->items[i];
        res.mtow_g += it->mass_g;
        res.category_mass_g[it->category] += it->mass_g;
        res.total_idle_power_w += it->power_w;

        sum_mx += it->mass_g * it->x_mm;
        sum_my += it->mass_g * it->y_mm;
        sum_mz += it->mass_g * it->z_mm;
    }

    if (res.mtow_g > 0.0f) {
        res.cg_x_mm = sum_mx / res.mtow_g;
        res.cg_y_mm = sum_my / res.mtow_g;
        res.cg_z_mm = sum_mz / res.mtow_g;

        for (int c = 0; c < CAT_COUNT; ++c) {
            res.category_fraction[c] = (res.category_mass_g[c] / res.mtow_g) * 100.0f;
        }

        float dx = res.cg_x_mm - budget->cot_x_mm;
        float dy = res.cg_y_mm - budget->cot_y_mm;
        res.cg_offset_mm = sqrtf(dx * dx + dy * dy);

        float total_max_thrust = budget->motor_count * budget->max_thrust_per_motor_g;
        res.twr = total_max_thrust / res.mtow_g;

        res.is_balanced = (res.cg_offset_mm <= 3.0f);
        res.is_twr_sufficient = (res.twr >= 1.8f);
        res.is_battery_fraction_ok = (res.category_fraction[CAT_BATTERY] <= 55.0f);
    }

    return res;
}

void budget_print_report(const WeightBudget* budget, const BudgetAnalysis* a) {
    printf("=================================================================\n");
    printf("              ІНЖЕНЕРНИЙ ЗВІТ ВАГОВОГО БЮДЖЕТУ                   \n");
    printf("=================================================================\n");
    printf("%-30s | %10s | %14s\n", "Категорія", "Маса (г)", "Частка MTOW (%)");
    printf("-----------------------------------------------------------------\n");

    for (int c = 0; c < CAT_COUNT; ++c) {
        printf("%-30s | %10.1f | %13.1f%%\n",
               CATEGORY_NAMES[c], a->category_mass_g[c], a->category_fraction[c]);
    }
    printf("-----------------------------------------------------------------\n");
    printf("%-30s | %10.1f | %13.1f%%\n", "ПОВНА ЗЛІТНА МАСА (MTOW)", a->mtow_g, 100.0f);
    printf("=================================================================\n");

    printf("Центр тяжіння (CG):      X = %+.1f мм, Y = %+.1f мм, Z = %+.1f мм\n",
           a->cg_x_mm, a->cg_y_mm, a->cg_z_mm);
    printf("Центр тяги (CoT):        X = %+.1f мм, Y = %+.1f мм\n",
           budget->cot_x_mm, budget->cot_y_mm);
    printf("Зсув CG відносно CoT:    Δ = %.2f мм [%s]\n",
           a->cg_offset_mm, a->is_balanced ? "OK: Збалансовано" : "УВАГА: Перекіс > 3 мм");

    printf("Тягооснащеність (TWR):   %.2f:1 [%s]\n",
           a->twr, a->is_twr_sufficient ? "OK: Запас тяги достатній" : "КРИТИЧНО: TWR < 1.8");
    printf("Частка акумулятора:      %.1f%% [%s]\n",
           a->category_fraction[CAT_BATTERY],
           a->is_battery_fraction_ok ? "OK: Оптимальна" : "УВАГА: Ризик перевантаження");
    printf("Споживання електроніки:  %.1f Вт (постійне бортове навантаження)\n",
           a->total_idle_power_w);
    printf("=================================================================\n");
}

int main(void) {
    WeightBudget uav;
    // Квадрокоптер X4, 4 мотори з макс. тягою 1850 г кожен, центр тяги у (0, 0)
    budget_init(&uav, 4, 1850.0f, 0.0f, 0.0f);

    budget_add(&uav, "Термальна камера + Gimbal", CAT_PAYLOAD,    380.0f,  45.0f,   0.0f, -20.0f, 12.0f);
    budget_add(&uav, "Бортовий комп'ютер SBC",   CAT_PAYLOAD,     85.0f,  10.0f,   0.0f,  10.0f, 15.0f);
    budget_add(&uav, "Батарея Li-ion 6S2P 21700",CAT_BATTERY,    860.0f, -22.0f,   0.0f,  25.0f,  0.0f);
    budget_add(&uav, "Мотори 2806.5 (4 шт)",     CAT_PROPULSION, 192.0f,   0.0f,   0.0f,   0.0f,  0.0f);
    budget_add(&uav, "ESC 4-in-1 55A",           CAT_PROPULSION,  28.0f,   0.0f,   0.0f,   5.0f,  1.5f);
    budget_add(&uav, "Пропелери 7.5x4.5 (4 шт)", CAT_PROPULSION,  36.0f,   0.0f,   0.0f,  15.0f,  0.0f);
    budget_add(&uav, "Політний контролер FC H7", CAT_AVIONICS,    14.0f,   0.0f,   0.0f,  12.0f,  3.0f);
    budget_add(&uav, "GNSS модуль + Compass",    CAT_AVIONICS,    18.0f, -50.0f,   0.0f,  45.0f,  1.2f);
    budget_add(&uav, "VTX 5.8GHz 2.5W + антена", CAT_AVIONICS,    32.0f, -40.0f,   0.0f,  20.0f, 11.0f);
    budget_add(&uav, "Приймач ELRS 868MHz",      CAT_AVIONICS,     4.0f, -30.0f,   0.0f,   8.0f,  0.5f);
    budget_add(&uav, "Карбонова рама 7 дюймів",  CAT_AIRFRAME,   165.0f,   0.0f,   0.0f,   0.0f,  0.0f);
    budget_add(&uav, "Кріплення, демпфери, TPU", CAT_AIRFRAME,    45.0f,   5.0f,   0.0f,   5.0f,  0.0f);
    budget_add(&uav, "Конструкторський резерв",  CAT_MARGIN,      80.0f,   0.0f,   0.0f,   0.0f,  0.0f);

    BudgetAnalysis report = budget_calculate(&uav);
    budget_print_report(&uav, &report);

    return 0;
}
