class NonTemplatePacketProcessor {
protected:
    size_t raw_serialize(void* dest, const void* src, size_t size) const {
        std::memcpy(dest, src, size);
        return size;
    }
};

template <typename Derived>
class FastSerializable : private NonTemplatePacketProcessor {
public:
    size_t serialize_to(uint8_t* destination) const {
        const auto& self = *static_cast<const Derived*>(this);
        return this->raw_serialize(destination, &self, sizeof(Derived));
    }
};
