namespace std {
    struct input_iterator_tag {};
    struct output_iterator_tag {};
    struct forward_iterator_tag : public input_iterator_tag {};
    struct bidirectional_iterator_tag : public forward_iterator_tag {};
    struct random_access_iterator_tag : public bidirectional_iterator_tag {};
    
    // Додано у C++20 для формалізації суцільної пам'яті
    struct contiguous_iterator_tag : public random_access_iterator_tag {};
}
