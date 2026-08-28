class random_device {
public:
    using result_type = unsigned int;

    explicit random_device(const std::string& token = /* implementation-defined */);
    static constexpr result_type min() { return 0; }
    static constexpr result_type max() { return std::numeric_limits<result_type>::max(); }
    double entropy() const noexcept;
    result_type operator()();

    // Заборона копіювання через системний ресурс
    random_device(const random_device&) = delete;
    random_device& operator=(const random_device&) = delete;
};
