// Ноги до 74HC595 (три штуки замість восьми сегментних):
static const SegPin PIN_DS   = { &PORTB, 1u << 0 };   // дані
static const SegPin PIN_SHCP = { &PORTB, 1u << 1 };   // такт зсуву
static const SegPin PIN_STCP = { &PORTB, 1u << 2 };   // засувка виходів

static inline void pin_hi(SegPin p) { *p.port |=  p.mask; }
static inline void pin_lo(SegPin p) { *p.port &= ~p.mask; }

// Виставити байт сегментів через зсувний регістр.
static void put_segments_595(uint8_t seg)
{
    // Заштовхуємо 8 бітів, старшим уперед (біт7=dp першим).
    for (int8_t i = 7; i >= 0; i--) {
        if (seg & (1u << i)) pin_hi(PIN_DS);   // біт на лінію даних
        else                 pin_lo(PIN_DS);
        pin_hi(PIN_SHCP);                      // фронт такту — біт заповз
        pin_lo(PIN_SHCP);
    }
    pin_hi(PIN_STCP);                          // засувка — усі 8 бітів на виходи разом
    pin_lo(PIN_STCP);
}
