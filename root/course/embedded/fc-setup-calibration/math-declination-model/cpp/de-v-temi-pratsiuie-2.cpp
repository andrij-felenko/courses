// очікуване з моделі (за координатами GNSS):
const float F_expect = 0.50f;    // гаус
const float I_expect = 66.0f;    // градуси

// виміряне магнітометром (уже відкалібрований вектор поля, гаус):
vec3_t m = compass_field_calibrated();     // {mx, my, mz} у системі апарата, рівень

float F_meas = sqrtf(m.x*m.x + m.y*m.y + m.z*m.z);   // виміряна напруженість
float H_meas = sqrtf(m.x*m.x + m.y*m.y);             // горизонтальна складова
float I_meas = atan2f(m.z, H_meas) * 180.0f/3.14159f; // виміряне нахилення

// узгодженість — обидві величини мусять збігтися з моделлю в межах допуску:
bool field_ok = fabsf(F_meas - F_expect) < 0.15f * F_expect;   // напруженість ±15%
bool incl_ok  = fabsf(I_meas - I_expect) < 15.0f;              // нахилення ±15°

if (!field_ok || !incl_ok) {
    // компас не узгоджений з очікуваним полем Землі — не пускати в політ
    arming_deny("compass field inconsistent with WMM");
}
