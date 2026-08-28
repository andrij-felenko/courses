struct TradeOrder {
    uint64_t order_id;
    double price;
    uint32_t volume;
    std::string client_id;

    void serialize_to(BinaryBuffer& buf) const {
        modern_cpp20::serialize(buf, order_id);
        modern_cpp20::serialize(buf, price);
        modern_cpp20::serialize(buf, volume);
        modern_cpp20::serialize(buf, client_id);
    }
};
