/* c */
typedef struct {
    double X;     /* Північна складова [нТл] (North component) */
    double Y;     /* Східна складова [нТл] (East component) */
    double Z;     /* Вертикальна складова [нТл] (Down component, > 0 вниз) */
    double H;     /* Горизонтальна складова [нТл] H = √(X² + Y²) */
    double F;     /* Повний модуль індукції [нТл] F = √(H² + Z²) */
    double I;     /* Кут магнітного нахилу [градуси] Inclination (-90..+90°) */
    double D;     /* Кут магнітного схилення [градуси] Declination (-180..+180°) */
    double GV;    /* Грідовий азимут [градуси] (Grid Variation для полярних карт) */
} wmm_elements_t;
