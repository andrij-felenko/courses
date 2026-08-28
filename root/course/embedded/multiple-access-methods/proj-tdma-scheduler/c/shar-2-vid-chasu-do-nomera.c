static volatile uint64_t g_epoch_us = 0;   // T₀: момент початку поточного кадру

// Куди ми зараз потрапили всередині кадру.
typedef struct {
    uint8_t  slot;        // номер поточного вікна, 0..N_SLOTS-1
    uint32_t into_us;     // скільки мкс минуло від початку цього вікна
} frame_pos_t;

static frame_pos_t where_in_frame(uint64_t now) {
    uint64_t since_epoch = now - g_epoch_us;        // мкс від T₀
    uint32_t in_frame    = (uint32_t)(since_epoch % FRAME_US);  // у межах кадру
    frame_pos_t p;
    p.slot    = (uint8_t)(in_frame / SLOT_US);
    p.into_us = in_frame % SLOT_US;
    return p;
}
