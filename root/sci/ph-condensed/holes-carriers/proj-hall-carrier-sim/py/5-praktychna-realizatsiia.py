#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Моделювання траєкторій носіїв заряду та формування поля Холла
у p- та n-напівпровідниках при перехресних E та B полях.
"""

import numpy as np
import matplotlib.pyplot as plt

# Фізичні константи
ELEM_CHARGE = 1.602e-19       # Кл (елементарний заряд)
MASS_ELECTRON = 9.109e-31      # кг (маса вільного електрона)
EPSILON_0 = 8.854e-12          # Ф/м (електрична стала)
EPSILON_SI = 11.7              # відносна діелектрична проникність Si

class SemiconductorHallSim:
    def __init__(self, carrier_type='hole', num_particles=1000):
        self.carrier_type = carrier_type
        self.N = num_particles
        
        # Геометрія зразка (м)
        self.L = 1e-3          # довжина 1 мм
        self.W = 0.2e-3        # ширина 0.2 мм
        
        # Зовнішні поля
        self.E_x = 1000.0      # В/м (поздовжнє поле)
        self.B_z = 0.5         # Тл (магнітна індукція)
        
        # Параметри носіїв (кремній при 300K)
        if carrier_type == 'hole':
            self.q = +ELEM_CHARGE
            self.m_eff = 0.45 * MASS_ELECTRON   # ефективна маса важкої дірки
            self.mobility = 0.045               # м²/(В·с) рухливість дірок
        elif carrier_type == 'electron':
            self.q = -ELEM_CHARGE
            self.m_eff = 0.26 * MASS_ELECTRON   # ефективна маса електрона
            self.mobility = 0.145               # м²/(В·с) рухливість електронів
        else:
            raise ValueError("Невідомий тип носія. Очікується 'hole' або 'electron'")
            
        # Час релаксації імпульсу τ = m* μ / |q|
        self.tau = (self.m_eff * self.mobility) / ELEM_CHARGE
        
        # Початковий стан ансамблю частинок
        self.reset_particles()
        
    def reset_particles(self):
        """Ініціалізація рівномірного розподілу частинок у зразку."""
        self.pos_x = np.random.uniform(0, self.L * 0.2, self.N)
        self.pos_y = np.random.uniform(0.05 * self.W, 0.95 * self.W, self.N)
        
        # Початкова дрейфова швидкість
        v_drift_x = (self.q / abs(self.q)) * self.mobility * self.E_x
        self.vel_x = np.random.normal(v_drift_x, abs(v_drift_x) * 0.1, self.N)
        self.vel_y = np.random.normal(0.0, abs(v_drift_x) * 0.1, self.N)
        
        # Заряд на межах (Кл)
        self.q_bottom = 0.0
        self.q_top = 0.0
        self.E_y = 0.0
        
    def _equations_of_motion(self, vx, vy, E_y_current):
        """Права частина рівнянь руху Ньютона-Лоренца з розсіюванням."""
        # Сила електричного поля + сила Лоренца + сила розсіювання
        fx = self.q * self.E_x + self.q * vy * self.B_z - (self.m_eff * vx / self.tau)
        fy = self.q * E_y_current - self.q * vx * self.B_z - (self.m_eff * vy / self.tau)
        
        ax = fx / self.m_eff
        ay = fy / self.m_eff
        return ax, ay

    def step_rk4(self, dt):
        """Крок чисельного інтегрування методом Рунге-Кутти 4-го порядку."""
        # Поточне поперечне поле від накопиченого заряду на гранях
        E_y_curr = self.E_y
        
        # RK4 для швидкостей та координат
        ax1, ay1 = self._equations_of_motion(self.vel_x, self.vel_y, E_y_curr)
        
        vx_k2 = self.vel_x + 0.5 * dt * ax1
        vy_k2 = self.vel_y + 0.5 * dt * ay1
        ax2, ay2 = self._equations_of_motion(vx_k2, vy_k2, E_y_curr)
        
        vx_k3 = self.vel_x + 0.5 * dt * ax2
        vy_k3 = self.vel_y + 0.5 * dt * ay2
        ax3, ay3 = self._equations_of_motion(vx_k3, vy_k3, E_y_curr)
        
        vx_k4 = self.vel_x + dt * ax3
        vy_k4 = self.vel_y + dt * ay3
        ax4, ay4 = self._equations_of_motion(vx_k4, vy_k4, E_y_curr)
        
        # Оновлення швидкостей
        self.vel_x += (dt / 6.0) * (ax1 + 2*ax2 + 2*ax3 + ax4)
        self.vel_y += (dt / 6.0) * (ay1 + 2*ay2 + 2*ay3 + ay4)
        
        # Оновлення координат
        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt
        
        # Крайові умови на бічних стінках y = 0 та y = W
        bottom_hits = self.pos_y <= 0
        top_hits = self.pos_y >= self.W
        
        if np.any(bottom_hits):
            self.q_bottom += np.sum(bottom_hits) * self.q
            self.pos_y[bottom_hits] = 0.0
            self.vel_y[bottom_hits] = 0.0
            
        if np.any(top_hits):
            self.q_top += np.sum(top_hits) * self.q
            self.pos_y[top_hits] = self.W
            self.vel_y[top_hits] = 0.0
            
        # Розрахунок оновленого електричного поля Холла E_y
        # E_y = Q / (eps * eps0 * L)
        dq_surf = (self.q_bottom - self.q_top) / 2.0
        self.E_y = dq_surf / (EPSILON_SI * EPSILON_0 * self.L * 1e3)

    def run_simulation(self, total_time=5e-11, num_steps=500):
        """Запуск симуляції та збір часових залежностей."""
        dt = total_time / num_steps
        time_arr = np.linspace(0, total_time, num_steps)
        
        ey_history = np.zeros(num_steps)
        vx_avg_history = np.zeros(num_steps)
        vy_avg_history = np.zeros(num_steps)
        
        for i in range(num_steps):
            self.step_rk4(dt)
            ey_history[i] = self.E_y
            vx_avg_history[i] = np.mean(self.vel_x)
            vy_avg_history[i] = np.mean(self.vel_y)
            
        return time_arr, ey_history, vx_avg_history, vy_avg_history

def compare_holes_and_electrons():
    """Порівняльний аналіз динаміки дірок та електронів у полі Холла."""
    sim_hole = SemiconductorHallSim(carrier_type='hole', num_particles=2000)
    sim_elec = SemiconductorHallSim(carrier_type='electron', num_particles=2000)
    
    t_h, ey_h, vx_h, vy_h = sim_hole.run_simulation(total_time=1e-10, num_steps=600)
    t_e, ey_e, vx_e, vy_e = sim_elec.run_simulation(total_time=1e-10, num_steps=600)
    
    # Побудова графіків результатів
    fig, axes = plt.subplots(2, 1, figsize=(9, 8))
    
    # 1. Залежність поля Холла E_y від часу
    axes[0].plot(t_h * 1e12, ey_h / 1e3, 'r-', label='Дірки (p-тип, q = +e)', linewidth=2)
    axes[0].plot(t_e * 1e12, ey_e / 1e3, 'b--', label='Електрони (n-тип, q = -e)', linewidth=2)
    axes[0].axhline(0, color='gray', linestyle=':', alpha=0.7)
    axes[0].set_xlabel('Час (пікосекунди, ps)')
    axes[0].set_ylabel('Поле Холла E_y (кВ/м)')
    axes[0].set_title('Динаміка встановлення поля Холла E_y(t)')
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend(loc='best')
    
    # 2. Дрейфова швидкість поздовжнього руху vx
    axes[1].plot(t_h * 1e12, vx_h / 1e3, 'r-', label='Дірки: v_x > 0 (у напрямку E_x)', linewidth=2)
    axes[1].plot(t_e * 1e12, vx_e / 1e3, 'b--', label='Електрони: v_x < 0 (проти E_x)', linewidth=2)
    axes[1].axhline(0, color='gray', linestyle=':', alpha=0.7)
    axes[1].set_xlabel('Час (пікосекунди, ps)')
    axes[1].set_ylabel('Дрейфова швидкість v_x (км/с)')
    axes[1].set_title('Поздовжня дрейфова швидкість носіїв')
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend(loc='best')
    
    plt.tight_layout()
    plt.savefig('hall_simulation_results.png', dpi=300)
    print("Симуляцію успішно завершено. Графіки збережено у 'hall_simulation_results.png'.")

if __name__ == '__main__':
    compare_holes_and_electrons()
