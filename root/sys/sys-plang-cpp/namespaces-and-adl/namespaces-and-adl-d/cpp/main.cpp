namespace lib {
    struct W {};
    void log(W, int);          // знаходиться лише через ADL
}

void log(lib::W, long);        // знаходиться звичайним пошуком

int main() {
    lib::W w;
    log(w, 1);                 // → lib::log(W, int)
}
