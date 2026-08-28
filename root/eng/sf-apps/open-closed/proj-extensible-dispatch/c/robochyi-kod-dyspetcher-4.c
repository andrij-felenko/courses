#include <stdio.h>

int main(void) {
    long cart = 100000;                       // 1000.00 грн у копійках

    PercentParams tenoff  = { .percent = 10 };
    FlatParams    fifty    = { .amount  = 5000 };          // −50.00 грн
    LoyaltyParams loyal    = { .percent = 5, .cap = 3000 };// −5%, але ≤ 30.00 грн

    printf("%ld\n", apply_discount(DISC_PERCENT, cart, &tenoff)); // 10000  (−100.00)
    printf("%ld\n", apply_discount(DISC_FLAT,    cart, &fifty));  //  5000  (−50.00)
    printf("%ld\n", apply_discount(DISC_LOYALTY, cart, &loyal));  //  3000  (стеля вдарила: 5% = 5000 > 3000)
    printf("%ld\n", apply_discount(DISC_COUNT,   cart, NULL));    //     0  (невідомий вид, межу зловили)
    return 0;
}
