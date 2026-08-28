class seed_seq {
public:
    using result_type = uint_least32_t;

    seed_seq() noexcept;
    template<typename InputIt> seed_seq(InputIt first, InputIt last);
    seed_seq(std::initializer_list<result_type> il);

    template<typename RandomIt> void generate(RandomIt begin, RandomIt end);
    size_t size() const noexcept;
    template<typename OutputIt> void param(OutputIt dest) const;

    seed_seq(const seed_seq&) = delete;
    seed_seq& operator=(const seed_seq&) = delete;
};
