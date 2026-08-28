// 1) новий вид у enum — перед DISC_COUNT:
//    ... DISC_LOYALTY, DISC_BIRTHDAY, DISC_COUNT

// 2) нова структура параметрів і новий обробник — окремо, нікого не чіпаючи:
typedef struct { long amount; } BirthdayParams;
static long disc_birthday(long total, const void *p) {
    (void)total;
    return ((const BirthdayParams *)p)->amount;
}

// 3) один рядок у таблицю:
//    [DISC_BIRTHDAY] = disc_birthday,
