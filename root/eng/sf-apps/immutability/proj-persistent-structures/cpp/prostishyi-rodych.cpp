// COW-вектор (спрощено, суть — у гілці «хочу писати»):
template <typename T>
class CowVector {
    std::shared_ptr<std::vector<T>> data_;   // спільний буфер
public:
    const T& operator[](size_t i) const { return (*data_)[i]; }   // читання — дешеве, зі спільного

    void set(size_t i, T v) {                                     // запис — тут і ховається ціна
        if (data_.use_count() > 1)                // на буфер дивиться ще хтось?
            data_ = std::make_shared<std::vector<T>>(*data_);     // так → ПОВНА копія, O(n)
        (*data_)[i] = std::move(v);               // тепер буфер лише мій — пишу на місці
    }
};
