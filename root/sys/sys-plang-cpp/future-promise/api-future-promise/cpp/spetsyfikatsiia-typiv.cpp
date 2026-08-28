namespace std {

enum class future_errc {
    broken_promise = 1,
    future_already_retrieved = 2,
    promise_already_satisfied = 3,
    no_state = 4
};

const error_category& future_category() noexcept;

make_error_code(future_errc e) noexcept;
make_error_condition(future_errc e) noexcept;

class future_error : public logic_error {
public:
    explicit future_error(error_code ec);
    const error_code& code() const noexcept;
    const char* what() const noexcept override;
};

} // namespace std
