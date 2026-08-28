class IVirtualProcessor {
public:
    virtual ~IVirtualProcessor() = default;
    virtual bool validate() const = 0;
    virtual uint32_t compute_checksum() const = 0;
    virtual size_t serialize_to(uint8_t* destination) const = 0;
    virtual void trace_status(const char* action) const = 0;
};

class VirtualOrderSingle : public IVirtualProcessor {
public:
    uint64_t order_id{0};
    uint64_t account_id{0};
    double price{0.0};
    uint32_t quantity{0};
    uint8_t side{1};

    bool validate() const override {
        return order_id > 0 && account_id > 0 && price > 0.0 && quantity > 0;
    }

    uint32_t compute_checksum() const override {
        const uint8_t* ptr = reinterpret_cast<const uint8_t*>(this);
        uint32_t sum = 0;
        for (size_t i = 0; i < sizeof(VirtualOrderSingle); ++i) {
            sum = (sum << 5) + sum + ptr[i];
        }
        return sum;
    }

    size_t serialize_to(uint8_t* destination) const override {
        std::memcpy(destination, this, sizeof(VirtualOrderSingle));
        return sizeof(VirtualOrderSingle);
    }

    void trace_status(const char* action) const override {
        std::cout << "[TRACE] Virtual Action: " << action << "\n";
    }
};
