// Опис одного сегмента: куди він фізично припаяний.
typedef struct {
    volatile uint8_t *port;   // регістр порту (напр. &PORTB)
    uint8_t           mask;   // маска ноги в цьому порту (напр. 1<<3)
} SegPin;

// Порядок ЗБІГАЄТЬСЯ з порядком бітів у байті: [0]=a ... [7]=dp.
// ↓↓↓  Ці адреси/ноги — приклад; підстав СВОЮ реальну розводку.  ↓↓↓
static const SegPin SEG[8] = {
    { &PORTB, 1u << 0 },   // a
    { &PORTB, 1u << 1 },   // b
    { &PORTB, 1u << 2 },   // c
    { &PORTD, 1u << 5 },   // d
    { &PORTD, 1u << 6 },   // e
    { &PORTD, 1u << 7 },   // f
    { &PORTC, 1u << 0 },   // g
    { &PORTC, 1u << 1 },   // dp
};

// Виставити байт seg (біт i → сегмент SEG[i]) на реальні ніжки.
static void put_segments(uint8_t seg)
{
    for (uint8_t i = 0; i < 8; i++) {
        if (seg & (1u << i))
            *SEG[i].port |=  SEG[i].mask;   // сегмент горить → нога у «1»
        else
            *SEG[i].port &= ~SEG[i].mask;   // сегмент згас  → нога у «0»
    }
}
