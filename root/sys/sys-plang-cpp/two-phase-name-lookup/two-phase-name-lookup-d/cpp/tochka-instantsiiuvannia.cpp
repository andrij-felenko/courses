#include <iostream>

// ── Контекст визначення шаблону (Фаза 1) ──────────────────────────────────
template <typename T>
void execute_pipeline(T obj) {
    // process_item(obj) — ЗАЛЕЖНИЙ виклик, бо obj має тип T.
    // Пошук імені process_item відкладено до Фази 2.
    process_item(obj);
}

// ── Модуль користувача (між шаблоном і main) ─────────────────────────────
namespace physics {
    struct Particle {
        double mass = 1.0;
    };

    // Функція оголошена ПІСЛЯ шаблону execute_pipeline,
    // але всередині асоційованого простору physics!
    void process_item(const Particle& p) {
        std::cout << "Processing particle with mass: " << p.mass << "\n";
    }
}

// ── Точка інстанціювання (POI) ─────────────────────────────────────────────
int main() {
    physics::Particle p;
    // Виклик інстанціює execute_pipeline<physics::Particle>.
    // POI розміщується перед main().
    execute_pipeline(p);
}
