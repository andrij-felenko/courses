class OrderSingle : public Validatable<OrderSingle>,
                    public Checksummable<OrderSingle>,
                    public Serializable<OrderSingle>,
                    public Traceable<OrderSingle> {
public:
    uint64_t order_id{0};
    uint64_t account_id{0};
    double price{0.0};
    uint32_t quantity{0};
    uint8_t side{1}; // 1 = Buy, 2 = Sell

    bool validate_impl() const {
        return order_id > 0 && account_id > 0 && price > 0.0 && quantity > 0;
    }
};
