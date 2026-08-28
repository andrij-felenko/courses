typedef struct {
    AnimMode mode;
    ShapeFn  shape;
    uint32_t durationMs;
    uint8_t  repeats;     // скільки разів повторити цей крок (для ONCE)
} AnimStep;

typedef struct {
    uint8_t        pin;
    bool           invert;
    const AnimStep *steps;   // масив кроків (зазвичай у флеш, const)
    uint8_t        count;    // скільки кроків
    uint8_t        cur;      // поточний крок
    uint8_t        left;     // скільки повторів поточного кроку лишилось
    int            slot;     // який слот зайнято (-1 = нічого не грає)
} AnimQueue;

static AnimQueue queues[4];   // до чотирьох незалежних послідовностей
