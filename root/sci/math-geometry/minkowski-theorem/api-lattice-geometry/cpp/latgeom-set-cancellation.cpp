namespace latgeom {

struct CancellationToken {
    std::atomic<bool>* flag{nullptr};
    uint64_t check_interval{1000};
};

void set_cancellation_token(LatticeBasis& basis, CancellationToken token) noexcept;

} // namespace latgeom
