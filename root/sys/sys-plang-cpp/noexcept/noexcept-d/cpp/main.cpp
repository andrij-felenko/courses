class Slow {                              // без обіцянки
    std::vector<double> data_;
public:
    Slow(Slow&& o) : data_(std::move(o.data_)) {}
    Slow(const Slow&) = default;
};

class Fast {                              // з обіцянкою
    std::vector<double> data_;
public:
    Fast(Fast&& o) noexcept : data_(std::move(o.data_)) {}
    Fast(const Fast&) = default;
};
