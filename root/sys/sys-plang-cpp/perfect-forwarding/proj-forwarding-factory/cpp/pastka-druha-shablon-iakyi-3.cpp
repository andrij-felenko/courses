class GuestCpp17 {
public:
    template <class S,
              class = std::enable_if_t<
                  !std::is_base_of_v<GuestCpp17, std::decay_t<S>> &&
                   std::is_constructible_v<std::string, S>>>
    explicit GuestCpp17(S&& src) : name_(std::forward<S>(src)) {}

    GuestCpp17(const GuestCpp17&) = default;
    GuestCpp17(GuestCpp17&&) noexcept = default;

    const std::string& name() const { return name_; }
private:
    std::string name_;
};
