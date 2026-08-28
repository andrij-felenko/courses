const float U0    = 14.8f;    // напруга без навантаження, В
const float R_INT = 0.020f;   // внутрішній опір пакета, Ом
const float I_PK  = 80.0f;    // піковий сумарний струм, А

float u_sag  = U0 - I_PK * R_INT;        // напруга під піком, В
float sag_pct = (U0 - u_sag) / U0 * 100.0f;

// оберти ~ пропорційні напрузі, тяга ~ квадрат обертів
// частка тяги, що лишилась = (u_sag/U0)^2
float rpm_ratio    = u_sag / U0;
float thrust_ratio = rpm_ratio * rpm_ratio;
float thrust_loss_pct = (1.0f - thrust_ratio) * 100.0f;
