struct Binding {
    int& target;
};

int inspect(Binding* b, int* next_val) {
    int first = b->target;
    
    b->~Binding();
    new (b) Binding{*next_val}; // нове посилання на іншу змінну
    
    // Помилка: використання старого вказівника b без launder
    int second = b->target;
    return first + second;
}
