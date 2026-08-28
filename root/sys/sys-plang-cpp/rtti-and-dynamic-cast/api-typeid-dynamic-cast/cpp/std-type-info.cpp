namespace std {
  class type_info {
  public:
    virtual ~type_info();
    constexpr bool operator==(const type_info& rhs) const noexcept;  // constexpr з C++23
    bool           before(const type_info& rhs) const noexcept;
    size_t         hash_code() const noexcept;                       // C++11
    const char*    name() const noexcept;
    type_info(const type_info&)            = delete;
    type_info& operator=(const type_info&) = delete;
  };
}
