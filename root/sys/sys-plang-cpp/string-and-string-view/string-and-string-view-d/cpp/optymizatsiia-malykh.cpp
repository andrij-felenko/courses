// Концептуальна структура std::string у 64-бітній системі (sizeof = 32 байти)
class string {
    union {
        struct {
            char*       ptr;
            std::size_t size;
            std::size_t capacity;
        } heap;

        struct {
            char        buf[23];
            unsigned char sso_size; // Або прапорець у старшому байті
        } sso;
    };
};
