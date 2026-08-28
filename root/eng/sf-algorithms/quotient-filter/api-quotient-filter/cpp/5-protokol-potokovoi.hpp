struct ReconstructedHash {
    size_t quotient;
    uint8_t remainder;
    [[nodiscard]] uint64_t full_hash(size_t r_bits) const noexcept {
        return (static_cast<uint64_t>(quotient) << r_bits) | remainder;
    }
};

class QuotientFilterIterator {
public:
    explicit QuotientFilterIterator(const QuotientFilter& qf);
    [[nodiscard]] bool has_next() const noexcept;
    ReconstructedHash next();
private:
    const QuotientFilter& qf_;
    size_t curr_slot_ = 0;
    size_t curr_fq_ = 0;
};
