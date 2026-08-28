// Сучасна реалізація для C++20 (Concepts & Requires & Subsumption)

// Визначення концептів інтерфейсів
template<typename T>
concept HasMemberSerialize = requires(const T& obj, Buffer& buf) {
    { obj.serialize(buf) } -> std::same_as<void>;
};

template<typename T>
concept HasAdlSerialize = requires(const T& obj, Buffer& buf) {
    { serialize(buf, obj) } -> std::same_as<void>;
};

template<typename T>
concept IterableContainer = requires(const T& c) {
    c.begin();
    c.end();
    typename T::value_type;
};

template<typename T>
concept TriviallyRaw = std::is_trivially_copyable_v<T>;

// 1. Гілка з власним методом
void write_data(Buffer& buf, const HasMemberSerialize auto& obj) {
    std::cout << "[Concept: Member] Виклик obj.serialize(buf)\n";
    obj.serialize(buf);
}

// 2. Гілка з ADL
void write_data(Buffer& buf, const HasAdlSerialize auto& obj) 
    requires (!HasMemberSerialize<decltype(obj)>) 
{
    std::cout << "[Concept: ADL] Виклик serialize(buf, obj)\n";
    serialize(buf, obj);
}

// 3. Гілка контейнерів
void write_data(Buffer& buf, const IterableContainer auto& container)
    requires (!HasMemberSerialize<decltype(container)> && !HasAdlSerialize<decltype(container)>)
{
    std::cout << "[Concept: Container] Серіалізація елементів\n";
    uint32_t sz = static_cast<uint32_t>(container.size());
    const uint8_t* sz_ptr = reinterpret_cast<const uint8_t*>(&sz);
    buf.insert(buf.end(), sz_ptr, sz_ptr + sizeof(sz));
    for (const auto& item : container) {
        write_data(buf, item);
    }
}

// 4. Гілка сирих байтів
void write_data(Buffer& buf, const TriviallyRaw auto& val)
    requires (!HasMemberSerialize<decltype(val)> && 
              !HasAdlSerialize<decltype(val)> && 
              !IterableContainer<decltype(val)>)
{
    std::cout << "[Concept: Raw] Прямий запис байтів\n";
    const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&val);
    buf.insert(buf.end(), ptr, ptr + sizeof(val));
}
