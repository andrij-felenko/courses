// coupled_sim.hpp — Сучасний C++20 клас симуляції зв'язаних осциляторів
#pragma once
#include <vector>
#include <numeric>
#include <cmath>
#include <stdexcept>
#include <span>

class CoupledChainCPP {
public:
    CoupledChainCPP(size_t num_masses, double mass, double spring_k, double damping = 0.0)
        : m_k(spring_k), m_damping(damping),
          m_masses(num_masses, mass),
          m_pos(num_masses, 0.0),
          m_vel(num_masses, 0.0),
          m_acc(num_masses, 0.0)
    {
        if (num_masses == 0) {
            throw std::invalid_argument("Кількість мас повинна бути > 0");
        }
        compute_accelerations();
    }

    void set_initial_displacement(size_t index, double value) {
        if (index < m_pos.size()) {
            m_pos[index] = value;
            compute_accelerations();
        }
    }

    void step(double dt) {
        const size_t n = m_pos.size();
        
        // 1. Оновлення координат і проміжних швидкостей
        for (size_t i = 0; i < n; ++i) {
            m_pos[i] += m_vel[i] * dt + 0.5 * m_acc[i] * dt * dt;
            m_vel[i] += 0.5 * m_acc[i] * dt;
        }
        
        // 2. Обчислення сил у нових позиціях
        compute_accelerations();
        
        // 3. Остаточне оновлення швидкостей
        for (size_t i = 0; i < n; ++i) {
            m_vel[i] += 0.5 * m_acc[i] * dt;
        }
    }

    [[nodiscard]] double total_energy() const noexcept {
        double e_kin = 0.0;
        double e_pot = 0.0;
        const size_t n = m_pos.size();

        for (size_t i = 0; i < n; ++i) {
            e_kin += 0.5 * m_masses[i] * m_vel[i] * m_vel[i];
            
            const double left_pos = (i == 0) ? 0.0 : m_pos[i - 1];
            const double delta = m_pos[i] - left_pos;
            e_pot += 0.5 * m_k * delta * delta;
        }
        const double delta_end = 0.0 - m_pos.back();
        e_pot += 0.5 * m_k * delta_end * delta_end;

        return e_kin + e_pot;
    }

    [[nodiscard]] std::span<const double> positions() const noexcept { return m_pos; }
    [[nodiscard]] std::span<const double> velocities() const noexcept { return m_vel; }

private:
    void compute_accelerations() noexcept {
        const size_t n = m_pos.size();
        for (size_t i = 0; i < n; ++i) {
            const double left_pos = (i == 0) ? 0.0 : m_pos[i - 1];
            const double right_pos = (i == n - 1) ? 0.0 : m_pos[i + 1];
            
            const double f_spring = -m_k * (m_pos[i] - left_pos) - m_k * (m_pos[i] - right_pos);
            const double f_damp = -m_damping * m_vel[i];
            
            m_acc[i] = (f_spring + f_damp) / m_masses[i];
        }
    }

    double m_k;
    double m_damping;
    std::vector<double> m_masses;
    std::vector<double> m_pos;
    std::vector<double> m_vel;
    std::vector<double> m_acc;
};
:::

## 4. Детальний аналіз ООП реалізації мовою C++20

Об'єктно-орієнтована версія мовою C++20 реалізована у вигляді класу `CoupledChainCPP`. Клас гарантує підтримку ідіоми RAII (*Resource Acquisition Is Initialization*): усі динамічні масиви зберігаються у стандартних контейнерах `std::vector<double>`, що повністю виключає необхідність виклику ручних операторів `delete` або функцій `free()`.

Основні архітектурні переваги C++20 реалізації:
- **Конструктор із валідацією параметрів:** Якщо користувач передає нульову кількість мас `num_masses == 0`, конструктор викидає виключення `std::invalid_argument`. Це унеможливлює створення об'єкта у некоректному стані.
- **Використання `std::span` для безпечного доступу:** Методи `positions()` та `velocities()` повертають легковагі представлення `std::span<const double>`. Це дозволяє зовнішньому коду читати масиви координат і швидкостей без копіювання пам'яті й без ризику випадкового пошкодження внутрішнього стану класу.
- **Атрибути `[[nodiscard]]` та `noexcept`:** Методи обчислення енергії та доступу позначені як `noexcept`, що дає компілятору можливість виконувати глибоку оптимізацію інлайн-розгортання без генерації додаткового коду обробки винятків.

## 5. Спектральний аналіз та проекція на нормальні координати

Для аналізу того, які саме нормальні моди збуджено у чисельному розрахунку, використовується процедура модальної проекції.

Нехай з аналітичного чи матричного розв'язку відома модальна матриця `T = [v_1 | v_2 | ... | v_N]`. Тоді на кожному кроці симуляції ми можемо обчислити поточні значення нормальних координат `η_r(t)` шляхом матрично-векторного множення:
