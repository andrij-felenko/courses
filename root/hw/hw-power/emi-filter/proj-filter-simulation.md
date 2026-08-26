# Розрахунок АЧХ затухання вхідного ЕМС-фільтра для CM та DM завад

Проєктування вхідного ЕМС-фільтра неможливо виконати лише за спрощеними формулами ідеальних LC-ланок, оскільки реальне затухання завад у діапазоні 150 кГц – 30 МГц критично залежить від паразитних параметрів компонентів (еквівалентної послідовної індуктивності ESL конденсаторів, міжвиткової ємності EPC дроселів) та частотно-залежного імпедансу еквівалента мережі LISN. Цей алгоритм моделює повний тракт поширення диференціальних (DM) і синфазних (CM) завад методом комплексних вузлових провідностей, розраховує частотну характеристику внесених втрат (Insertion Loss) та перевіряє досягнення цільових рівнів затухання за стандартами CISPR.

### Математична модель вимірювального тракту

Внесені втрати фільтра `IL(f)` (англ. *Insertion Loss*) визначаються як логарифмічне відношення напруги завади на вимірювальному порту 50 Ом без фільтра `V_unfiltered` до напруги з підключеним фільтром `V_filtered`:

```
IL(f) = 20 · log10(|V_unfiltered(f) / V_filtered(f)|)
```

Для коректного розрахунку модель враховує такі комплексні імпеданси:

1. **Еквівалент мережі LISN (CISPR 16-1-2 / 50 мкГн + 5 Ом || 50 Ом).**
LISN (Line Impedance Stabilization Network) виконує три взаємопов'язані функції:
- забезпечує стабільний нормований імпеданс 50 Ом для високочастотних сигналів завад у смузі 150 кГц – 30 МГц незалежно від реального стану та довжини живильної електромережі;
- ізолює вимірювальний приймач від зовнішніх шумів, що надходять з боку живильної підстанції;
- блокує постійну складову або напругу промислової частоти 50/60 Гц за допомогою розділового конденсатора `0.1 мкФ`, пропускаючи на вхід аналізатора спектра лише високочастотний шум.

Комплексний імпеданс однієї фази LISN відносно землі:
```
Z_lisn(s) = (s·L_lisn + R_iso) || (R_meas + 1 / (s·C_coup))
```
де `L_lisn = 50 мкГн`, `R_iso = 5 Ом`, `C_coup = 0.1 мкФ`, `R_meas = 50 Ом`.
- Для диференціальної завади (DM) дві фази LISN включені послідовно у вимірювальний контур: `Z_source,DM = 2 · Z_lisn` (на високих частотах прямує до 100 Ом).
- Для синфазної завади (CM) обидві фази включені паралельно відносно землі: `Z_source,CM = Z_lisn / 2` (на високих частотах прямує до 25 Ом).

2. **Реальний конденсатор (X- та Y-конденсатори).**
Плівкові поліпропіленові (MKP) та металопаперові X-конденсатори, а також керамічні Y-конденсатори мають власні виводи та внутрішню геометрію обкладок, що додають послідовний паразитний опір (ESR) та послідовну паразитну індуктивність (ESL):
```
Z_cap(s) = R_esr + s·L_esl + 1 / (s·C)
```
На частоті власного резонансу `f_srf = 1 / (2π · √(C · L_esl))` ємнісний опір повністю компенсується індуктивним, а вище цієї частоти конденсатор перестає шунтувати заваду й поводиться як індуктивність, погіршуючи затухання зі швидкістю +20 дБ/дек.

3. **Реальний дросель (CMC та індуктивність розсіювання L_leak).**
Синфазний дросель на тороїдальному феритовому осерді має значну кількість витків, між якими утворюється розподілена паразитні ємність, що зводиться до еквівалентної паралельної ємності (EPC):
```
Z_ind(s) = (s·L + R_dcr) || (1 / (s·C_epc))
```
Міжвиткова ємність `C_epc` шунтує індуктивність вище власної резонансної частоти (типово 500 кГц – 2 МГц), через що на частотах 10–30 МГц імпеданс дроселя різко падає, створюючи прямий шлях для проходження синфазного струму завади.

### Правило узгодження імпедансів: вибір топології фільтра

Загальна ефективність фільтра залежить від співвідношення імпедансів між фільтром, джерелом завади та навантаженням. Фільтр працює як відбивач та розсіювач енергії завади, тому діє правило максимального неузгодження імпедансів:
- До вузла з **низьким імпедансом** (наприклад, низькоімпедансний вхідний керамічний конденсатор перетворювача для DM завади) фільтр повинен повертатися **високим імпедансом** (індуктивністю);
- До вузла з **високим імпедансом** (наприклад, джерело синфазної напруги з малою паразитною ємністю радіатора) фільтр повинен повертатися **низьким імпедансом** (конденсатором Y у землю).

Саме тому стандартний вхідний фільтр має симетричну П-подібну або подвійну Г-подібну структуру: X-конденсатори стоять по обидва боки від дроселя, забезпечуючи низький імпеданс шунтування як у бік мережі, так і в бік входу перетворювача.

### Програмна реалізація симулятора

:::tabs
```cpp
#include <iostream>
#include <iomanip>
#include <complex>
#include <vector>
#include <cmath>
#include <string_view>

namespace emi {

using Complex = std::complex<double>;
constexpr double PI = 3.14159265358979323846;

// Модель LISN 50 мкГн / 50 Ом за стандартом CISPR 16
struct LisnModel {
    double l_choke = 50.0e-6; // 50 мкГн
    double r_iso   = 5.0;     // 5 Ом
    double c_coup  = 0.1e-6;  // 0.1 мкФ
    double r_meas  = 50.0;    // 50 Ом вхідний опір приймача

    [[nodiscard]] Complex impedance(double f) const {
        double w = 2.0 * PI * f;
        Complex s(0.0, w);
        Complex z_branch1 = s * l_choke + r_iso;
        Complex z_branch2 = r_meas + 1.0 / (s * c_coup);
        return (z_branch1 * z_branch2) / (z_branch1 + z_branch2);
    }
};

// Реальний конденсатор з ESR та ESL
struct RealCapacitor {
    double c   = 0.0;
    double esr = 0.0;
    double esl = 0.0;

    [[nodiscard]] Complex impedance(double f) const {
        double w = 2.0 * PI * f;
        Complex s(0.0, w);
        return esr + s * esl + 1.0 / (s * c);
    }
};

// Реальний індуктор з DCR та паразитною ємністю EPC
struct RealInductor {
    double l   = 0.0;
    double dcr = 0.0;
    double epc = 0.0; // Еквівалентна паралельна ємність

    [[nodiscard]] Complex impedance(double f) const {
        double w = 2.0 * PI * f;
        Complex s(0.0, w);
        Complex z_lr = s * l + dcr;
        if (epc <= 0.0) {
            return z_lr;
        }
        Complex y_epc = s * epc;
        return z_lr / (Complex(1.0, 0.0) + z_lr * y_epc);
    }
};

// Параметри вхідного ЕМС-фільтра
struct EmiFilterDesign {
    RealCapacitor cx1;    // Вхідний X-конденсатор
    RealCapacitor cx2;    // Вихідний X-конденсатор
    RealCapacitor cy;     // Y-конденсатор (два в схемі)
    RealInductor  l_cm;   // Синфазний дросель
    RealInductor  l_leak; // Індуктивність розсіювання (DM)
    double r_damp = 0.0;  // Резистор демпфування Міддлбрука
    double c_damp = 0.0;  // Конденсатор демпфування Міддлбрука
};

class FilterSimulator {
public:
    explicit FilterSimulator(EmiFilterDesign design)
        : design_(std::move(design)) {}

    // Розрахунок внесених втрат для диференціальної завади (DM)
    [[nodiscard]] double calculate_il_dm(double f, double r_load = 50.0) const {
        Complex z_lisn_dm = 2.0 * lisn_.impedance(f); // 2 гілки LISN послідовно
        Complex z_cx1 = design_.cx1.impedance(f);
        Complex z_cx2 = design_.cx2.impedance(f);
        Complex z_leak = 2.0 * design_.l_leak.impedance(f); // Індуктивність розсіювання в обох проводах

        // Паралельний демпфувальний ланцюжок
        double w = 2.0 * PI * f;
        Complex z_damp = design_.r_damp + 1.0 / (Complex(0.0, w) * design_.c_damp);

        // Напруга без фільтра (дільник джерело - навантаження)
        Complex v_unfiltered = r_load / (z_lisn_dm + r_load);

        // Матричний вузловий аналіз П-фільтра
        // Вузол 1 (вхід фільтра до LISN), Вузол 2 (вихід фільтра до навантаження)
        Complex y_in = 1.0 / z_lisn_dm + 1.0 / z_cx1 + 1.0 / z_leak;
        Complex y_out = 1.0 / z_leak + 1.0 / z_cx2 + 1.0 / z_damp + 1.0 / r_load;
        Complex y_m = -1.0 / z_leak;

        // Визначник системи вузлових рівнянь
        Complex det = y_in * y_out - y_m * y_m;
        // Напруга на виході при струмі одиничного джерела I_s = 1 / Z_lisn_dm
        Complex v_filtered = (1.0 / z_lisn_dm) * (-y_m) / det;

        double ratio = std::abs(v_unfiltered / v_filtered);
        return 20.0 * std::log10(std::max(ratio, 1.0e-6));
    }

    // Розрахунок внесених втрат для синфазної завади (CM)
    [[nodiscard]] double calculate_il_cm(double f, double r_cm_source = 25.0) const {
        Complex z_lisn_cm = lisn_.impedance(f) / 2.0; // 2 гілки LISN паралельно
        Complex z_cm_choke = design_.l_cm.impedance(f);
        // Два Y-конденсатори з L та N у землю підключені паралельно для CM
        RealCapacitor cy_total = design_.cy;
        cy_total.c *= 2.0;
        cy_total.esr /= 2.0;
        cy_total.esl /= 2.0;
        Complex z_cy_pair = cy_total.impedance(f);

        Complex v_unfiltered = z_lisn_cm / (r_cm_source + z_lisn_cm);

        // L-ланка: Choke послідовно + CY-паралельно
        Complex z_total_shunt = z_cy_pair;
        Complex z_ser = z_cm_choke;

        Complex v_filtered = (v_unfiltered * z_total_shunt) / 
                             (z_ser + z_total_shunt + z_lisn_cm);

        double ratio = std::abs(v_unfiltered / v_filtered);
        return 20.0 * std::log10(std::max(ratio, 1.0e-6));
    }

private:
    EmiFilterDesign design_;
    LisnModel lisn_;
};

} // namespace emi

int main() {
    using namespace emi;

    // Конфігурація компонентів промислового фільтра
    EmiFilterDesign filter{
        .cx1 = {.c = 0.47e-6, .esr = 0.015, .esl = 8.0e-9},  // 0.47 мкФ X2
        .cx2 = {.c = 0.22e-6, .esr = 0.020, .esl = 6.0e-9},  // 0.22 мкФ X2
        .cy  = {.c = 3.3e-9,  .esr = 0.050, .esl = 3.5e-9},  // 3.3 нФ Y2
        .l_cm = {.l = 4.7e-3, .dcr = 0.040, .epc = 15.0e-12}, // 4.7 мГн CMC (EPC 15 пФ)
        .l_leak = {.l = 25.0e-6, .dcr = 0.020, .epc = 3.0e-12}, // 25 мкГн розсіювання
        .r_damp = 1.0,      // 1.0 Ом демпфер Міддлбрука
        .c_damp = 2.2e-6    // 2.2 мкФ блокувальна ємність
    };

    FilterSimulator sim(filter);

    std::cout << "========================================================\n";
    std::cout << " АЧХ затухання вхідного ЕМС-фільтра (Insertion Loss)\n";
    std::cout << "========================================================\n";
    std::cout << std::setw(12) << "Частота" 
              << std::setw(16) << "IL_DM (дБ)" 
              << std::setw(16) << "IL_CM (дБ)" 
              << std::setw(14) << "Статус\n";
    std::cout << "--------------------------------------------------------\n";

    const std::vector<double> test_freqs = {
        10.0e3, 50.0e3, 100.0e3, 150.0e3, 300.0e3, 500.0e3,
        1.0e6, 2.0e6, 5.0e6, 10.0e6, 20.0e6, 30.0e6
    };

    for (double f : test_freqs) {
        double il_dm = sim.calculate_il_dm(f);
        double il_cm = sim.calculate_il_cm(f);

        std::string_view status = (il_dm >= 30.0 && il_cm >= 40.0) ? "PASS (OK)" : "MARGINAL";
        if (f < 150.0e3) status = "INFO";

        std::cout << std::setw(10) << std::fixed << std::setprecision(1) << (f / 1.0e3) << " кГц"
                  << std::setw(15) << std::setprecision(2) << il_dm
                  << std::setw(15) << std::setprecision(2) << il_cm
                  << std::setw(14) << status << "\n";
    }
    std::cout << "========================================================\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

// Модель LISN 50 мкГн / 50 Ом
typedef struct {
    double l_choke;
    double r_iso;
    double c_coup;
    double r_meas;
} LisnModel;

double complex lisn_impedance(const LisnModel* lisn, double f) {
    double w = 2.0 * PI * f;
    double complex s = I * w;
    double complex z_b1 = s * lisn->l_choke + lisn->r_iso;
    double complex z_b2 = lisn->r_meas + 1.0 / (s * lisn->c_coup);
    return (z_b1 * z_b2) / (z_b1 + z_b2);
}

typedef struct {
    double c;
    double esr;
    double esl;
} RealCapacitor;

double complex cap_impedance(const RealCapacitor* cap, double f) {
    double w = 2.0 * PI * f;
    double complex s = I * w;
    return cap->esr + s * cap->esl + 1.0 / (s * cap->c);
}

typedef struct {
    double l;
    double dcr;
    double epc;
} RealInductor;

double complex ind_impedance(const RealInductor* ind, double f) {
    double w = 2.0 * PI * f;
    double complex s = I * w;
    double complex z_lr = s * ind->l + ind->dcr;
    if (ind->epc <= 0.0) return z_lr;
    double complex y_epc = s * ind->epc;
    return z_lr / (1.0 + z_lr * y_epc);
}

typedef struct {
    RealCapacitor cx1;
    RealCapacitor cx2;
    RealCapacitor cy;
    RealInductor  l_cm;
    RealInductor  l_leak;
    double r_damp;
    double c_damp;
    LisnModel lisn;
} EmiFilter;

double calculate_il_dm(const EmiFilter* filter, double f, double r_load) {
    double complex z_lisn_dm = 2.0 * lisn_impedance(&filter->lisn, f);
    double complex z_cx1 = cap_impedance(&filter->cx1, f);
    double complex z_cx2 = cap_impedance(&filter->cx2, f);
    double complex z_leak = 2.0 * ind_impedance(&filter->l_leak, f);

    double w = 2.0 * PI * f;
    double complex z_damp = filter->r_damp + 1.0 / (I * w * filter->c_damp);

    double complex v_unfiltered = r_load / (z_lisn_dm + r_load);

    double complex y_in = 1.0 / z_lisn_dm + 1.0 / z_cx1 + 1.0 / z_leak;
    double complex y_out = 1.0 / z_leak + 1.0 / z_cx2 + 1.0 / z_damp + 1.0 / r_load;
    double complex y_m = -1.0 / z_leak;

    double complex det = y_in * y_out - y_m * y_m;
    double complex v_filtered = (1.0 / z_lisn_dm) * (-y_m) / det;

    double ratio = cabs(v_unfiltered / v_filtered);
    if (ratio < 1.0e-6) ratio = 1.0e-6;
    return 20.0 * log10(ratio);
}

double calculate_il_cm(const EmiFilter* filter, double f, double r_cm_source) {
    double complex z_lisn_cm = lisn_impedance(&filter->lisn, f) / 2.0;
    double complex z_cm_choke = ind_impedance(&filter->l_cm, f);

    RealCapacitor cy_total = filter->cy;
    cy_total.c *= 2.0;
    cy_total.esr /= 2.0;
    cy_total.esl /= 2.0;
    double complex z_cy_pair = cap_impedance(&cy_total, f);

    double complex v_unfiltered = z_lisn_cm / (r_cm_source + z_lisn_cm);
    double complex z_total_shunt = z_cy_pair;
    double complex z_ser = z_cm_choke;

    double complex v_filtered = (v_unfiltered * z_total_shunt) / 
                                (z_ser + z_total_shunt + z_lisn_cm);

    double ratio = cabs(v_unfiltered / v_filtered);
    if (ratio < 1.0e-6) ratio = 1.0e-6;
    return 20.0 * log10(ratio);
}

int main(void) {
    EmiFilter filter = {
        .cx1 = {.c = 0.47e-6, .esr = 0.015, .esl = 8.0e-9},
        .cx2 = {.c = 0.22e-6, .esr = 0.020, .esl = 6.0e-9},
        .cy  = {.c = 3.3e-9,  .esr = 0.050, .esl = 3.5e-9},
        .l_cm = {.l = 4.7e-3, .dcr = 0.040, .epc = 15.0e-12},
        .l_leak = {.l = 25.0e-6, .dcr = 0.020, .epc = 3.0e-12},
        .r_damp = 1.0,
        .c_damp = 2.2e-6,
        .lisn = {.l_choke = 50.0e-6, .r_iso = 5.0, .c_coup = 0.1e-6, .r_meas = 50.0}
    };

    printf("========================================================\n");
    printf(" АЧХ затухання вхідного ЕМС-фільтра (Insertion Loss)\n");
    printf("========================================================\n");
    printf("%10s %16s %16s %14s\n", "Частота", "IL_DM (дБ)", "IL_CM (дБ)", "Статус");
    printf("--------------------------------------------------------\n");

    const double freqs[] = {
        10.0e3, 50.0e3, 100.0e3, 150.0e3, 300.0e3, 500.0e3,
        1.0e6, 2.0e6, 5.0e6, 10.0e6, 20.0e6, 30.0e6
    };
    const int num_freqs = sizeof(freqs) / sizeof(freqs[0]);

    for (int i = 0; i < num_freqs; i++) {
        double f = freqs[i];
        double il_dm = calculate_il_dm(&filter, f, 50.0);
        double il_cm = calculate_il_cm(&filter, f, 25.0);

        const char* status = (il_dm >= 30.0 && il_cm >= 40.0) ? "PASS (OK)" : "MARGINAL";
        if (f < 150.0e3) status = "INFO";

        printf("%8.1f кГц %15.2f %15.2f %14s\n", f / 1.0e3, il_dm, il_cm, status);
    }
    printf("========================================================\n");

    return 0;
}
```
:::

### Типові інженерні пастки при аналізі результатів симуляції

1. **Падіння затухання вище власного резонансу конденсаторів (SRF).** Якщо X-конденсатор ємністю 0.47 мкФ має паразитну індуктивність виводів та доріжок `ESL = 8 нГн`, його власний резонанс настає на частоті:
```
f_srf = 1 / (2π · √(0.47×10⁻⁶ · 8×10⁻⁹)) ≈ 2.6 МГц
```
Вище цієї частоти імпеданс конденсатора зростає як `ω·ESL`, і він перестає ефективно шунтувати заваду. На частоті 30 МГц опір конденсатора становить вже `2π · 30×10⁶ · 8×10⁻⁹ ≈ 1.5 Ом` замість теоретичних 0.01 Ом. Для виправлення паралельно великому плівковому конденсатору встановлюють високочастотний керамічний конденсатор ємністю 10–47 нФ (типорозмір 0603 або 0805 з ESL менше 0.8 нГн), який бере на себе фільтрацію в смузі 5–30 МГц.

2. **Вплив міжвиткової ємності дроселя (EPC).** Для синфазного дроселя з індуктивністю `4.7 мГн` паразитні 15 пФ міжвиткової ємності утворюють паралельний антирезонанс на частоті `f ≈ 600 кГц`. На вищих частотах імпеданс дроселя стрімко падає, через що затухання синфазної завади на частотах 10–30 МГц погіршується на 20–30 дБ порівняно з ідеальною моделлю. Для зниження EPC застосовують секційну намотку з перегородкою на осерді або розділяють фільтрацію на два послідовні дроселі: низькочастотний тороїд на високопроникному фериті (MnZn) та високочастотний дросель на фериті з низькою проникністю (NiZn).

3. **Взаємна магнітна та ємнісна індукція між входом і виходом фільтра.** Якщо вхідні й вихідні провідники розташовані паралельно на платі, паразитний взаємний зв'язок передає високочастотний шум в обхід усіх фільтрувальних ланок. Навіть 1 пФ паразитної ємності зв'язку між доріжками обмежує максимальне затухання фільтра на рівні 50–60 дБ на частоті 30 МГц. Тому топологія плати вимагає суворого просторового розділення входу та виходу й суцільного захисного екрану заземлення під компонентами фільтра.
