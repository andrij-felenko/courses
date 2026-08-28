namespace sgh {

class OrdinalException : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

class OverflowException final : public OrdinalException {
public:
    OverflowException() : OrdinalException("Arithmetic integer overflow in SGH evaluation") {}
};

class ParseException final : public OrdinalException {
private:
    size_t position_;
public:
    ParseException(const std::string& msg, size_t pos)
        : OrdinalException(msg + " at position " + std::to_string(pos)), position_(pos) {}
    [[nodiscard]] size_t position() const noexcept { return position_; }
};

class InvalidOrdinalException final : public OrdinalException {
public:
    explicit InvalidOrdinalException(const std::string& msg) : OrdinalException(msg) {}
};

}
