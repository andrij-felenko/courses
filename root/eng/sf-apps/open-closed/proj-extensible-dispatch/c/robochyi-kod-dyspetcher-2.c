// Види знижки — індекси в таблиці. Порядок тут ЗАДАЄ відповідність рядкам.
typedef enum {
    DISC_PERCENT = 0,
    DISC_FLAT,
    DISC_LOYALTY,
    DISC_COUNT            // не вид знижки, а «скільки їх усього» — завжди останній
} DiscountKind;

// ТАБЛИЦЯ ДИСПЕТЧЕРИЗАЦІЇ: рядок «вид → функція».
// Додати новий вид знижки = дописати ОДИН рядок сюди (+ написати обробник вище).
static const DiscountFn DISCOUNT_TABLE[DISC_COUNT] = {
    [DISC_PERCENT] = disc_percent,
    [DISC_FLAT]    = disc_flat,
    [DISC_LOYALTY] = disc_loyalty,
};
