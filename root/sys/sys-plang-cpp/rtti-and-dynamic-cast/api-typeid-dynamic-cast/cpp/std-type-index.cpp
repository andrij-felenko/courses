namespace std {
  class type_index {
  public:
    type_index(const type_info& rhs) noexcept;          // неявний, навмисно
    bool             operator==(const type_index&) const noexcept;
    strong_ordering  operator<=>(const type_index&) const noexcept;  // C++20
    bool             operator<(const type_index&) const noexcept;    // і >, <=, >=
    size_t           hash_code() const noexcept;
    const char*      name() const noexcept;
  };
  template<> struct hash<type_index>;   // повертає rhs.hash_code()
}
