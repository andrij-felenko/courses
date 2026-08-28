import numpy as np

def simulate_eddy_braking(mass=0.5, sigma_0=5.8e7, alpha_temp=0.00393, c_heat=385.0,
                           thickness=0.005, length=0.15, width=0.10, b_field=0.8, 
                           field_length=0.10, c_geo=0.25, k_air=0.01,
                           v0=5.0, pos0=-0.05, temp0=20.0, dt=1e-4, t_max=0.2):
    """
    Симуляція індукційного гальмування Ленца з урахуванням температури провідника.
    """
    time_pts = np.arange(0, t_max, dt)
    n = len(time_pts)
    
    pos = np.zeros(n)
    vel = np.zeros(n)
    temp = np.zeros(n)
    force = np.zeros(n)
    power = np.zeros(n)
    
    pos[0] = pos0
    vel[0] = v0
    temp[0] = temp0
    
    for i in range(n - 1):
        # Обчислення активної площі перекриття
        entry = pos[i]
        exit_edge = pos[i] - length
        
        start_in = np.clip(entry, 0.0, field_length)
        end_in = np.clip(exit_edge, 0.0, field_length)
        active_len = max(0.0, start_in - end_in)
        active_area = active_len * width
        
        # Температурна залежність провідності
        current_sigma = sigma_0 / (1.0 + alpha_temp * (temp[i] - 20.0))
        
        # Гальмівна сила Ленца
        f_eddy = c_geo * current_sigma * thickness * active_area * (b_field**2) * vel[i]
        f_air = k_air * vel[i] * abs(vel[i])
        total_f = -(f_eddy + f_air)
        
        p_heat = f_eddy * vel[i]
        dT = (p_heat * dt) / (mass * c_heat)
        
        force[i] = total_f
        power[i] = p_heat
        
        accel = total_f / mass
        vel[i+1] = max(0.0, vel[i] + accel * dt)
        pos[i+1] = pos[i] + vel[i+1] * dt
        temp[i+1] = temp[i] + dT
        
        if vel[i+1] <= 1e-4:
            pos[i+1:] = pos[i+1]
            vel[i+1:] = 0.0
            temp[i+1:] = temp[i+1]
            break
            
    return time_pts, pos, vel, temp, force, power

if __name__ == '__main__':
    t, x, v, temp, f, p = simulate_eddy_braking()
    e_kin_init = 0.5 * 0.5 * 5.0**2
    print(f"Початкова кінетична енергія: {e_kin_init:.2f} Дж")
    print(f"Максимальна гальмівна сила: {np.abs(f).max():.2f} Н")
    print(f"Максимальна потужність дисипації: {p.max():.2f} Вт")
    print(f"Фінальна температура пластини: {temp[-1]:.2f} °C (приріст: {temp[-1] - 20.0:.2f} K)")
