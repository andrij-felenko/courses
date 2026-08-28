template <typename T>
class CircularBuffer {
public:
    template <typename Iter>
    CircularBuffer(Iter first, Iter last);
};

// Явне правило виведення для ітераторів:
template <typename Iter>
CircularBuffer(Iter, Iter) -> CircularBuffer<typename std::iterator_traits<Iter>::value_type>;
