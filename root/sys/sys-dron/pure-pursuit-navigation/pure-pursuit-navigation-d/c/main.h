// стан апарата на цей такт (зі стеку локалізації)
float px, py, theta;     // позиція [м] і курс [рад]
float v;                 // поточна швидкість [м/с]
float gx, gy;            // ціль-точка на шляху (світові координати) [м]

// параметри апарата/налаштування
const float wheelbase   = 0.32f;   // колісна база [м]
const float k_look      = 0.9f;    // коеф. випередження [с]
const float L_min       = 0.4f;    // мінімальне випередження [м]
const float delta_max   = 0.5f;    // межа кута керма [рад]

// 1) випередження, пропорційне швидкості (з нижньою межею)
float L = k_look * v;
if (L < L_min) L = L_min;

// 2) бічний зсув цілі в системі апарата (поворот на -theta)
float dx = gx - px;
float dy = gy - py;
float x  = -sinf(theta) * dx + cosf(theta) * dy;

// 3) кривина дуги pure pursuit
float kappa = 2.0f * x / (L * L);

// 4) переклад у кут керма (велосипедна модель) + затиск межами
float delta = atanf(wheelbase * kappa);
if (delta >  delta_max) delta =  delta_max;
if (delta < -delta_max) delta = -delta_max;

steer_set(delta);         // видати наказ керму
