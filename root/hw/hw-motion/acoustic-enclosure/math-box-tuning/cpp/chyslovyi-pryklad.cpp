#include <cmath>
#include <print>

// Параметри Тіле–Смолла — просто з даташита
struct Driver {
    float fs;      // власна частота, Гц
    float vas;     // еквівалентний об'єм, літри
    float qts;     // повна добротність
};

// Об'єм закритого ящика під бажану Q_tc.
// Виводиться з V_box = V_as / (α² − 1), де α = Q_tc/Q_ts.
float sealed_volume_litres(const Driver& d, float qtc_target)
{
    float alpha = qtc_target / d.qts;       // у скільки разів піднімаємо Q
    float denom = alpha * alpha - 1.0f;     // α² − 1
    if (denom <= 0.0f) return -1.0f;        // Q_tc ≤ Q_ts недосяжна в ЗАКРИТОМУ ящику
    return d.vas / denom;
}

// Частота −3 дБ (для Батерворта Q_tc=0.707 вона дорівнює f_c).
float closed_box_fc(const Driver& d, float vbox_litres)
{
    return d.fs * std::sqrt(1.0f + d.vas / vbox_litres);
}

int main()
{
    Driver woofer{ .fs = 40.0f, .vas = 20.0f, .qts = 0.35f };

    float qtc  = 0.707f;
    float vbox = sealed_volume_litres(woofer, qtc);
    float fc   = closed_box_fc(woofer, vbox);

    std::println("Ціль Q_tc = {:.3f}", qtc);
    std::println("Об'єм коробки V_box = {:.1f} л", vbox);
    std::println("Частота в ящику f_c = {:.1f} Гц", fc);
}
