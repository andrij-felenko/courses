// Ідіоматичний еквівалент ітератора послідовного потоку у C++
template <typename T>
class SeqStreamIterator {
public:
    virtual ~SeqStreamIterator() = default;
    virtual std::optional<T> start(off_t& pos) = 0;
    virtual std::optional<T> next(off_t& pos) = 0;
    virtual void stop() = 0;
    virtual std::string render_item(const T& item) = 0;
};
