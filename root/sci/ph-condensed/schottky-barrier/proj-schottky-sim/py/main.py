import math
import numpy as np

class SchottkySimulator:
    """Модуль розрахунку та екстракції параметрів бар'єра Шотткі."""
    
    Q = 1.602176634e-19       # Заряд електрона (Кл)
    KB = 1.380649e-23         # Стала Больцмана (Дж/К)
    EPS0 = 8.8541878128e-14   # Діелектрична стала вакууму (Ф/см)

    def __init__(self, area_cm2=1.0e-3, rel_perm=11.7, richardson_a=112.0):
        self.area = area_cm2
        self.eps_s = rel_perm * self.EPS0
        self.a_star = richardson_a

    def generate_iv(self, phi_bn_ev=0.7, eta=1.05, rs_ohm=15.0, temp_k=300.0, v_max=0.6, steps=100):
        """Ґенерує вольт-амперну характеристику за моделлю термоелектронної емісії."""
        vt = (self.KB * temp_k) / self.Q
        is_sat = self.area * self.a_star * (temp_k ** 2) * math.exp(-phi_bn_ev / vt)
        
        voltages = np.linspace(0.0, v_max, steps)
        currents = np.zeros_like(voltages)
        
        for i, v in enumerate(voltages):
            # Чисельне розв'язання трансцендентного рівняння методом Ньютона-Рафсона
            curr = 1.0e-9
            for _ in range(20):
                v_diode = v - curr * rs_ohm
                f_val = curr - is_sat * (math.exp(v_diode / (eta * vt)) - 1.0)
                df_val = 1.0 + is_sat * (rs_ohm / (eta * vt)) * math.exp(v_diode / (eta * vt))
                step = f_val / df_val
                curr -= step
                if abs(step) < 1.0e-12:
                    break
            currents[i] = max(curr, 0.0)
            
        return voltages, currents

    def extract_cheung_params(self, voltages, currents, temp_k=300.0):
        """Екстрагує Rs та eta за допомогою функції Чуна dV/d(ln I)."""
        vt = (self.KB * temp_k) / self.Q
        ln_i = np.log(np.maximum(currents, 1.0e-12))
        
        # Обчислення чисельної похідної dV / d(ln I)
        dvdln_i = np.gradient(voltages, ln_i)
        
        # Вибір прямолінійної ділянки середня напруга
        mask = (voltages > 0.2) & (voltages < 0.5)
        if not np.any(mask):
            mask = np.ones_like(voltages, dtype=bool)
            
        rs_fit, eta_vt_fit = np.polyfit(currents[mask], dvdln_i[mask], 1)
        eta_fit = eta_vt_fit / vt
        
        return {"rs_ohm": rs_fit, "eta": eta_fit}

    def extract_cv_params(self, vr_array, c_array_pf, temp_k=300.0):
        """Екстрагує Nd та Vbi з вольт-фарадної характеристики (1/C² vs VR)."""
        vt = (self.KB * temp_k) / self.Q
        c_farad = np.array(c_array_pf) * 1.0e-12
        inv_c2 = 1.0 / (c_farad ** 2)
        
        # Лінійна регресія: inv_c2 = slope * VR + intercept
        slope, intercept = np.polyfit(vr_array, inv_c2, 1)
        
        # Nd = 2 / (q * eps_s * A² * slope)
        nd_cm3 = 2.0 / (self.Q * self.eps_s * (self.area ** 2) * slope)
        
        # Vbi = intercept / slope + Vt
        v_int = intercept / slope
        v_bi = v_int + vt
        
        return {"nd_cm3": nd_cm3, "v_bi_v": v_bi, "slope": slope}

# Демонстраційний запуск
if __name__ == "__main__":
    sim = SchottkySimulator(area_cm2=1.0e-3)
    v, i = sim.generate_iv(phi_bn_ev=0.72, eta=1.04, rs_ohm=10.0)
    print(f"Сгенеровано {len(v)} точок ВАХ. Струм при V=0.5В: {i[int(len(i)*0.83)]*1e3:.3f} мА")
