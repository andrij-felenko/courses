class Buffer {
    std::vector<char> data_;
public:
    const std::vector<char>& data() const&  { return data_; }              // об'єкт має ім'я
    std::vector<char>        data() &&      { return std::move(data_); }   // об'єкт тимчасовий
};

Buffer b;
auto& live = b.data();          // перший: посилання всередину живого b
auto  taken = makeBuffer().data();   // другий: вміст забрано з тимчасового
