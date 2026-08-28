// Допоміжний простір імен для ізоляції перевірки ADL
namespace adl_detection {
    // Фіктивні оголошення, щоб компілятор знав ім'я serialize під час первинного розбору
    void serialize();

    template<typename T, typename = void>
    struct has_adl_serialize : std::false_type {};

    template<typename T>
    struct has_adl_serialize<T, std::void_t<
        decltype(serialize(std::declval<Buffer&>(), std::declval<const T&>()))
    >> : std::true_type {};
}

template<typename T>
inline constexpr bool has_adl_serialize_v = adl_detection::has_adl_serialize<T>::value;
