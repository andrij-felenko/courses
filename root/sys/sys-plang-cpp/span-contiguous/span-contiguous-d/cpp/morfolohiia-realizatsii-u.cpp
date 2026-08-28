// Концептуальна схема реалізації libstdc++
template <typename _Tp, std::size_t _Extent>
class __span_base {
public:
    constexpr __span_base(_Tp* __ptr, std::size_t) noexcept : _M_ptr(__ptr) {}
    constexpr std::size_t _M_size() const noexcept { return _Extent; }
    _Tp* _M_ptr;
};

// Спеціалізація для dynamic_extent додає поле розміру
template <typename _Tp>
class __span_base<_Tp, std::dynamic_extent> {
public:
    constexpr __span_base(_Tp* __ptr, std::size_t __size) noexcept 
        : _M_ptr(__ptr), _M_size_val(__size) {}
    constexpr std::size_t _M_size() const noexcept { return _M_size_val; }
    _Tp* _M_ptr;
    std::size_t _M_size_val;
};
