import math

# Груповий час із масиву виміряних фаз phi[k] на сітці частот із кроком df (Гц).
# phi — у радіанах; результат tau[k] — у секундах. N точок.
# τг = −dφ/dω = −(Δφ) / (2π·Δf)  — центральна різниця між сусідами.
def group_delay_from_phase(phi, df):
    N = len(phi)
    two_pi_df = 2.0 * math.pi * df
    tau = [0.0] * N
    for k in range(1, N - 1):
        dphi = phi[k + 1] - phi[k - 1]      # різниця через дві точки (апертура 2·df)
        # розгортання стрибка ±2π, якщо фаза «перескочила» межу:
        if dphi >  math.pi: dphi -= 2.0 * math.pi
        if dphi < -math.pi: dphi += 2.0 * math.pi
        tau[k] = -dphi / (2.0 * two_pi_df)  # ділимо на 2·(2π·df): центральна різниця
    tau[0] = tau[1]                         # краї — копією сусіда
    tau[N - 1] = tau[N - 2]
    return tau
