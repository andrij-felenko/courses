#include <stdint.h>
#include <stdbool.h>

#define N_FRAMES   49        // стовпчиків у секундній спектрограмі
#define N_MEL      40        // мел-смуг у кадрі
#define HOP        2         // проганяти модель що HOP нових кадрів
#define KW_INDEX   3         // індекс нашого ключового слова у виході
#define THRESHOLD  0.85f     // поріг спрацювання за згладженою ймовірністю
#define REFRACTORY 15        // «спокій» після спрацювання, у кадрах

static float spectro[N_FRAMES][N_MEL];  // кільцевий буфер спектрограми
static int   head = 0;                   // куди писати наступний стовпчик
static int   since_run = 0;              // лічильник кадрів між проходами
static float smooth = 0.0f;              // згладжена ймовірність слова
static int   cooldown = 0;               // лишок періоду спокою, у кадрах

// викликається на КОЖЕН новий кадр звуку (≈ раз на 20 мс)
bool kws_on_frame(const float mel_column[N_MEL]) {
    // 1. дописати свіжий стовпчик, затерши найстаріший (кільце)
    for (int m = 0; m < N_MEL; m++)
        spectro[head][m] = mel_column[m];
    head = (head + 1) % N_FRAMES;

    if (cooldown > 0) cooldown--;        // доживаємо період спокою

    // 2. модель ганяємо не щокадру, а що HOP кадрів — заради тактів
    if (++since_run < HOP) return false;
    since_run = 0;

    // 3. один прохід мережі по поточній секунді (деталі — у proj-вставці)
    float probs[/*класів*/ 8];
    kws_invoke(spectro, head, probs);    // читає кільце з правильним початком

    // 4. згладити ймовірність нашого слова в часі (ковзне середнє)
    const float A = 0.4f;                // інертність згладжування
    smooth += A * (probs[KW_INDEX] - smooth);

    // 5. рішення: впевнено вище порогу І не в періоді спокою
    if (smooth > THRESHOLD && cooldown == 0) {
        cooldown = REFRACTORY;           // блокуємо повтори на це слово
        smooth   = 0.0f;                 // скидаємо, щоб не спрацювати ще раз
        return true;                     // ← ключове слово розпізнано
    }
    return false;
}
