template<typename BidirectionalIt>
class reverse_iterator {
public:
    using iterator_type = BidirectionalIt;

    explicit reverse_iterator(BidirectionalIt it) : current_(it) {}

    // Метод base() повертає базовий прямоточний ітератор
    BidirectionalIt base() const { return current_; }

    // Зворотний інкремент кличе декремент базового ітератора!
    reverse_iterator& operator++() {
        --current_;
        return *this;
    }

    // Розіменування читає елемент на один крок лівіше від current_!
    reference operator*() const {
        BidirectionalIt temp = current_;
        return *(--temp);
    }
private:
    BidirectionalIt current_;
};
