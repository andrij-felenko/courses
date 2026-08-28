// --- Варіант А: голі біти, «швидко й потворно» ---
GPIO.OUT_SET = (1u << 5);          // запалити ніжку 5

// --- Варіант Б: чиста абстракція ---
template <uint8_t PIN>
struct Pin {
    static void high() { GPIO.OUT_SET = (1u << PIN); }
};

Pin<5>::high();                     // те саме, але читабельно
