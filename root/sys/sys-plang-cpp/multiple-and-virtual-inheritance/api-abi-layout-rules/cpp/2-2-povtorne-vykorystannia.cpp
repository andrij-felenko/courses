struct Base {
    virtual ~Base() = default; // vptr: 8 байтів (зсув 0..7)
    int32_t val;               // 4 байти (зсув 8..11)
    // 4 байти tail padding (зсув 12..15)
};

struct Derived : public Base {
    int32_t extra; // Розміщується за зсувом 12 всередині tail padding Base!
    // sizeof(Derived) залишається 16 байтів замість 24!
};
