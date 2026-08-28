enum class Tier { Regular, Gold };

class Product {                                  // сутність: свій id, свій стан складу
public:
    Product(std::string id, Money unitPrice, int stock)
        : id_(std::move(id)), unitPrice_(std::move(unitPrice)), stock_(stock) {
        if (stock < 0) throw DomainError("залишок не буває від'ємний");
    }
    const Money& price() const { return unitPrice_; }
    int stock() const { return stock_; }
    void reserve(int qty) {                      // метод-команда: товар сам стереже склад
        if (qty <= 0)       throw DomainError("резервувати можна лише додатну кількість");
        if (qty > stock_)   throw DomainError("на складі лише " + std::to_string(stock_));
        stock_ -= qty;
    }
    const std::string& id() const { return id_; }
private:
    std::string id_;
    Money unitPrice_;
    int stock_;
};

class Customer {                                 // сутність: свій рівень лояльності
public:
    Customer(std::string id, Tier tier) : id_(std::move(id)), tier_(tier) {}
    int discountPercent() const { return tier_ == Tier::Gold ? 10 : 0; }  // знає свій відсоток
    const std::string& id() const { return id_; }
private:
    std::string id_;
    Tier tier_;
};

class OrderLine {                                // всередині агрегату замовлення
public:
    OrderLine(std::string productId, Money unitPrice, int qty)
        : productId_(std::move(productId)), unitPrice_(std::move(unitPrice)), qty_(qty) {
        if (qty <= 0) throw DomainError("кількість у позиції має бути додатна");
    }
    Money subtotal() const { return unitPrice_.times(qty_); }   // рахує сам, знімком ціни
    const std::string& productId() const { return productId_; }
private:
    std::string productId_;                      // товар — за id, а не покажчиком
    Money unitPrice_;                            // знімок ціни на мить додавання
    int qty_;
};
