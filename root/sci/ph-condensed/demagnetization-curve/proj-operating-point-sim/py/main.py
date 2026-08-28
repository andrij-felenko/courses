import math

class PermanentMagnetModel:
    def __init__(self, Br, Hcj, S=4.5, mu_rec=1.05, alpha_Br=-0.11, beta_Hcj=-0.50):
        """
        Модель кривої розмагнічування постійного магніту.
        Br: залишкова індукція при 20°C (Тл)
        Hcj: власна коерцитивність при 20°C (кА/м)
        S: коефіцієнт прямокутності петлі J(H)
        mu_rec: відносна магнітна проникність повернення (recoil permeability)
        alpha_Br: температурний коефіцієнт Br (%/°C)
        beta_Hcj: температурний коефіцієнт Hcj (%/°C)
        """
        self.MU_0_SCALE = 4.0 * math.pi * 1e-4  # Тл / (кА/м)
        self.Br_20 = Br
        self.Hcj_20 = Hcj
        self.S = S
        self.mu_rec = mu_rec
        self.alpha_Br = alpha_Br
        self.beta_Hcj = beta_Hcj

    def get_params_at_temp(self, temp_C):
        """Розрахунок температурно-коригованих параметрів Br та Hcj."""
        dt = temp_C - 20.0
        Br_t = self.Br_20 * (1.0 + (self.alpha_Br / 100.0) * dt)
        Hcj_t = self.Hcj_20 * (1.0 + (self.beta_Hcj / 100.0) * dt)
        return max(0.05, Br_t), max(10.0, Hcj_t)

    def J_val(self, H, Br_t, Hcj_t):
        """Інтринсивна намагніченість J(H) у Тл для від'ємного поля H (кА/м)."""
        ratio = 1.0 + (H / Hcj_t)
        if ratio < -2.0:
            return 0.0
        return Br_t * math.tanh(self.S * ratio)

    def B_val(self, H, Br_t, Hcj_t):
        """Сумарна індукція B(H) у Тл для від'ємного поля H (кА/м)."""
        return (self.MU_0_SCALE * H) + self.J_val(H, Br_t, Hcj_t)

    def find_operating_point(self, Pc, temp_C=20.0, H_ext=0.0):
        """
        Обчислення статичної робочої точки (H_op, B_op) та перевірка лінії повернення.
        Pc: коефіцієнт провідності |B/H|
        temp_C: температура середовища (°C)
        H_ext: додаткове зовнішнє розмагнічувальне поле від струму (кА/м, додатне за модулем)
        """
        Br_t, Hcj_t = self.get_params_at_temp(temp_C)
        
        # Границі бісекції для полем H (від від'ємних полів до 0)
        h_low = -Hcj_t * 1.6
        h_high = 0.0
        
        for _ in range(60):
            h_mid = (h_low + h_high) / 2.0
            b_mag = self.B_val(h_mid - H_ext, Br_t, Hcj_t)
            b_load = Pc * (-h_mid) * self.MU_0_SCALE
            
            if b_mag > b_load:
                h_high = h_mid
            else:
                h_low = h_mid

        h_op = (h_low + h_high) / 2.0
        h_net = h_op - H_ext
        b_op = self.B_val(h_net, Br_t, Hcj_t)
        
        # Точка згину (knee point)
        h_knee = -Hcj_t * (1.0 - (1.0 / self.S))
        is_below_knee = (h_net < h_knee)

        # Розрахунок лінії повернення (recoil line), якщо поле H_ext зникне
        b_recoil_r = 0.0
        if is_below_knee:
            # Магніт повертається вздовж лінії з нахилом mu_rec
            b_recoil_r = b_op - self.mu_rec * self.MU_0_SCALE * h_net
        else:
            b_recoil_r = Br_t

        return {
            "temp_C": temp_C,
            "Br_t": Br_t,
            "Hcj_t": Hcj_t,
            "H_op": h_op,
            "B_op": b_op,
            "H_knee": h_knee,
            "below_knee": is_below_knee,
            "Br_recoil": b_recoil_r,
            "delta_Br_loss": Br_t - b_recoil_r
        }

if __name__ == "__main__":
    magnet = PermanentMagnetModel(Br=1.30, Hcj=950.0, S=5.0, alpha_Br=-0.12, beta_Hcj=-0.55)
    
    print("=== Чисельне моделювання робочої точки NdFeB N42 ===")
    print("Температура | Br(Тл) | Hcj(кА/м) | H_op(кА/м) | B_op(Тл) | Стан стійкості")
    print("-" * 75)
    
    for temp in [20, 80, 120, 150]:
        res = magnet.find_operating_point(Pc=1.2, temp_C=temp, H_ext=50.0)
        status = "⚠️ НЕЗВОРОВНЕ РОЗМАГНІЧУВАННЯ!" if res["below_knee"] else "✅ СТАБІЛЬНО"
        print(f"  {temp:3d} °C     |  {res['Br_t']:.2f}  |   {res['Hcj_t']:5.1f}   |   {res['H_op']:6.1f}   |  {res['B_op']:.3f}  | {status}")
