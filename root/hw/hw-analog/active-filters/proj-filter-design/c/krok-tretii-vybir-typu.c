// Один «рецепт» ланки: множник частоти (f_ланки = fmul · fc) і добротність.
typedef struct { float fmul; float Q; } sk_recipe;

// Тип фільтра = впорядкований набір ланок (нижчий Q першим — економить запас).
typedef struct {
    const char  *name;
    const sk_recipe *stage;   // масив ланок
    uint8_t      order;       // порядок (2 на кожну ланку 2-го порядку)
    uint8_t      nstage;
} sk_filter_type;

// ── Другий порядок: одна ланка ───────────────────────────────────────────
static const sk_recipe BW2[]  = { {1.000f, 0.7071f} };           // Баттерворт
static const sk_recipe BE2[]  = { {1.274f, 0.5774f} };           // Бессель
static const sk_recipe CH2_1[]= { {0.863f, 0.9565f} };           // Чебишев 1 дБ

// ── Четвертий порядок: дві ланки, нижчий Q першим ────────────────────────
static const sk_recipe BW4[]  = { {1.000f, 0.5412f}, {1.000f, 1.3066f} };
static const sk_recipe BE4[]  = { {1.432f, 0.5219f}, {1.606f, 0.8055f} };
static const sk_recipe CH4_05[]={ {0.597f, 0.7051f}, {1.031f, 2.9406f} }; // 0.5 дБ
static const sk_recipe CH4_1[]= { {0.529f, 0.7846f}, {0.993f, 3.5600f} }; // 1 дБ

static const sk_filter_type FT_BW4 =
    { "Баттерворт-4", BW4, 4, 2 };
static const sk_filter_type FT_BE4 =
    { "Бессель-4",    BE4, 4, 2 };
static const sk_filter_type FT_CH4_1 =
    { "Чебишев-4 (1 дБ)", CH4_1, 4, 2 };
