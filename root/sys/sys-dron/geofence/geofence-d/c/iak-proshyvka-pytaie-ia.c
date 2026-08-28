// Спрощена перевірка циліндричної геозони навколо дому.
// dist_home_m() рахує відстань (метри) від поточної точки до HOME
// за формулою гаверсинусів; тут ми лише порівнюємо її з радіусом.

#define FENCE_RADIUS_M   300.0f   // радіус «бляшанки», метри
#define FENCE_ALT_MAX_M  120.0f   // стеля висоти, метри

bool inside_cylinder(float lat, float lon, float alt_m) {
    float d = dist_home_m(lat, lon);      // відстань до дому по горизонталі
    if (d > FENCE_RADIUS_M)   return false;   // вилетів за коло
    if (alt_m > FENCE_ALT_MAX_M) return false; // пробив стелю
    return true;                          // усередині і кола, і стелі
}
