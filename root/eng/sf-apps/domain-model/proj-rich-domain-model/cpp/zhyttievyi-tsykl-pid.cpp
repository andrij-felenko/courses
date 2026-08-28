enum class Status { Draft, Placed, Shipped, Cancelled };

class Order {
public:
    Order(std::string id, std::string customerId)
        : id_(std::move(id)), customerId_(std::move(customerId)) {}

    // ── команди: єдиний спосіб зрушити стан, і в кожній — вартовий ──
    void addLine(Product& product, int qty) {
        if (status_ != Status::Draft)
            throw DomainError("позиції можна додавати лише чернетці");
        product.reserve(qty);                            // розмова з Product: хай стереже склад
        lines_.emplace_back(product.id(), product.price(), qty);
    }

    void place(const Customer& customer) {
        if (status_ != Status::Draft)
            throw DomainError("оформити можна лише чернетку");
        if (lines_.empty())
            throw DomainError("порожнє замовлення оформити не можна");

        Money sum = Money::zero(lines_.front().subtotal().currency());
        for (const OrderLine& line : lines_)
            sum = sum.add(line.subtotal());              // OrderLine рахує сам, Money додає сам
        total_ = sum.withDiscountPercent(customer.discountPercent());  // Customer дає свій відсоток
        status_ = Status::Placed;                        // інваріант циклу — під замком самого Order
    }

    void ship() {
        if (status_ != Status::Placed)
            throw DomainError("відвантажити можна лише оформлене замовлення");
        status_ = Status::Shipped;
    }

    void cancel() {
        if (status_ != Status::Draft && status_ != Status::Placed)
            throw DomainError("скасувати можна лише чернетку або оформлене");
        status_ = Status::Cancelled;
    }

    // ── запити ──
    Status status() const { return status_; }
    const Money& total() const {
        if (!total_) throw DomainError("підсумок з'являється лише в оформленого замовлення");
        return *total_;
    }
private:
    std::string id_;
    std::string customerId_;                             // клієнт — за id, а не покажчиком
    Status status_ = Status::Draft;
    std::vector<OrderLine> lines_;
    std::optional<Money> total_;                         // підсумку нема, доки не оформлено
};
