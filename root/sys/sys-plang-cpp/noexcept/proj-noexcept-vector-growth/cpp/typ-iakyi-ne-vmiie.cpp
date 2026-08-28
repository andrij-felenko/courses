class MoveOnly {
public:
    explicit MoveOnly(std::size_t n) : data_(n, 1.0) { ++g.ctor; }

    MoveOnly(const MoveOnly&)            = delete;
    MoveOnly& operator=(const MoveOnly&) = delete;

    MoveOnly(MoveOnly&& o) : data_(std::move(o.data_)) { ++g.move; }   // без noexcept
    MoveOnly& operator=(MoveOnly&& o) {
        data_ = std::move(o.data_); ++g.move; return *this;
    }
    ~MoveOnly() { ++g.dtor; }

private:
    std::vector<double> data_;
};

static_assert(!std::is_copy_constructible_v<MoveOnly>);
static_assert(!std::is_nothrow_move_constructible_v<MoveOnly>);
