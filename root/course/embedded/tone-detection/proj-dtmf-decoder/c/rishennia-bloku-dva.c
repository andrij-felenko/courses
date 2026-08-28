// пороги-коефіцієнти (підбираються під тракт; це робочі стартові значення)
#define REL_THRESHOLD   0.10f   // два піки мусять нести >=10% енергії блоку
#define RIVAL_RATIO     0.50f   // другий у групі — не сильніший за половину переможця
#define TWIST_MAX       4.0f    // дозволене відношення power низького/високого тону
#define ENERGY_FLOOR    1.0f    // нижче цього блок вважаємо тишею (захист від ділення)

static const char dtmf_sym[4][4] = {
    { '1', '2', '3', 'A' },
    { '4', '5', '6', 'B' },
    { '7', '8', '9', 'C' },
    { '*', '0', '#', 'D' },
};

// розпізнати символ у готовому блоці; 0 — тон не впізнано (тиша/шум/каша)
char dtmf_classify(const dtmf_bank_t *b)
{
    // 0) тихий блок — навіть не рахуємо відносин (інакше ділимо майже на нуль)
    if (b->energy < ENERGY_FLOOR)
        return 0;

    float p[N_TONES];
    for (int i = 0; i < N_TONES; ++i)
        p[i] = g_power(&b->g[i]);

    // 1) найсильніший бін у кожній групі
    int row = 0, col = 4;
    for (int i = 1; i < 4; ++i) if (p[i] > p[row]) row = i;
    for (int i = 5; i < 8; ++i) if (p[i] > p[col]) col = i;

    // 2) відносний поріг: два переможці несуть вагому частку енергії блоку
    if (p[row] + p[col] < REL_THRESHOLD * b->energy)
        return 0;

    // 3) жодного зайвого тону: другий у групі помітно слабший за переможця
    float row2 = 0.0f, col2 = 0.0f;
    for (int i = 0; i < 4; ++i) if (i != row && p[i] > row2) row2 = p[i];
    for (int i = 4; i < 8; ++i) if (i != col && p[i] > col2) col2 = p[i];
    if (row2 > RIVAL_RATIO * p[row] || col2 > RIVAL_RATIO * p[col])
        return 0;

    // 4) twist: низький і високий тон не мають надто розходитися за силою
    float hi = p[col], lo = p[row];
    if (lo > TWIST_MAX * hi || hi > TWIST_MAX * lo)
        return 0;

    return dtmf_sym[row][col - 4];
}
