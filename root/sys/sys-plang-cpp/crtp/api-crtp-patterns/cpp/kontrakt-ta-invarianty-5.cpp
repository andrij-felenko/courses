template <typename Derived>
struct PropertyMap {
    static constexpr const char* name() noexcept {
        return Derived::type_name;
    }
    static constexpr uint32_t type_id() noexcept {
        return Derived::type_identifier;
    }
};

struct PacketA : PropertyMap<PacketA> {
    static constexpr const char* type_name = "PacketA";
    static constexpr uint32_t type_identifier = 0x1001;
};
