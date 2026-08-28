import numpy as np

# коефіцієнти моделі втрат (ті самі, що в тексті)
V_out = 3.3      # В    — регульована вихідна напруга
P_fix = 0.030    # Вт   — фіксовані втрати: спокій + затвор + осердя
k_sw  = 0.05     # Вт/А — комутаційні, ростуть ∝ I
R     = 0.20     # Ом   — провідні, ростуть ∝ I²

def p_loss(I):                       # повні втрати за струмом
    return P_fix + k_sw*I + R*I**2

def efficiency(I):                   # η = P_вих / (P_вих + P_втрат)
    p_out = V_out * I
    return p_out / (p_out + p_loss(I))

# логарифмічний прогін струму: 10 мА … 5 А
I   = np.logspace(np.log10(0.01), np.log10(5.0), 4000)
eta = efficiency(I)

j          = np.argmax(eta)          # чисельний пік
I_peak_num = I[j]
I_peak_ana = np.sqrt(P_fix / R)      # закрита форма: √(P_фікс/R)

print(f"чисельний пік:  I = {I_peak_num:.4f} А,  η = {eta[j]*100:.2f} %")
print(f"√(P_фікс/R):    I = {I_peak_ana:.4f} А,  η = {efficiency(I_peak_ana)*100:.2f} %")
