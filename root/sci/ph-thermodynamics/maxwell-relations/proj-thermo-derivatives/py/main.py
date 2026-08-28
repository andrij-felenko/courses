import numpy as np

class VdWGasPy:
    def __init__(self, a=0.137, b=3.87e-5, R=8.31446):
        self.a = a
        self.b = b
        self.R = R
        self.Cv_ideal = 2.5 * R

    def pressure(self, T, V):
        return (self.R * T) / (V - self.b) - self.a / (V ** 2)

    def verify_maxwell(self, T, V, h_T=1e-4):
        P_plus = self.pressure(T + h_T, V)
        P_minus = self.pressure(T - h_T, V)
        dPdT_num = (P_plus - P_minus) / (2.0 * h_T)
        
        dPdT_exact = self.R / (V - self.b)
        abs_err = abs(dPdT_num - dPdT_exact)
        
        P_val = self.pressure(T, V)
        int_press = T * dPdT_num - P_val
        exact_int_press = self.a / (V ** 2)
        
        return dPdT_num, abs_err, int_press, exact_int_press

def run_simulation():
    gas = VdWGasPy()
    T_arr = np.linspace(200.0, 600.0, 6)
    V_val = 1.0e-3 # 1 L/mol
    
    print(f"{'T (K)':>10} {'P (Па)':>15} {'(∂U/∂V)_T':>15} {'a/V² (Теорія)':>15} {'μ_JT (К/Па)':>15}")
    print("-" * 75)
    
    h_T, h_V = 1e-4, 1e-6
    for T in T_arr:
        P = gas.pressure(T, V_val)
        dPdT = (gas.pressure(T + h_T, V_val) - gas.pressure(T - h_T, V_val)) / (2.0 * h_T)
        dPdV = (gas.pressure(T, V_val + h_V) - gas.pressure(T, V_val - h_V)) / (2.0 * h_V)
        
        int_press = T * dPdT - P
        exact_int_press = gas.a / (V_val ** 2)
        
        dVdT_p = -dPdT / dPdV
        Cp = gas.Cv_ideal + T * (dPdT ** 2) / (-dPdV)
        mu_JT = (1.0 / Cp) * (T * dVdT_p - V_val)
        
        print(f"{T:10.2f} {P:15.4e} {int_press:15.4e} {exact_int_press:15.4e} {mu_JT:15.4e}")

if __name__ == "__main__":
    run_simulation()
