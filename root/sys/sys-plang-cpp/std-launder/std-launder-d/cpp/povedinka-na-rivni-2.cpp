int inspect_correct(Binding* b, int* next_val) {
    int first = b->target;
    
    b->~Binding();
    new (b) Binding{*next_val};
    
    Binding* lb = std::launder(b); // очищення інваріантів
    int second = lb->target;
    return first + second;
}
