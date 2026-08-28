#include <string>
#include <stdexcept>

// Замовлення — лише мішок даних: статус назовні, жодного правила всередині
class Order {
public:
    explicit Order(std::string id) : id_(std::move(id)), status_("new") {}

    std::string getStatus() const { return status_; }
    void setStatus(std::string s) { status_ = std::move(s); }

    const std::string& id() const { return id_; }

private:
    std::string id_;
    std::string status_;   // "new" | "paid" | "shipped" | "cancelled"
};

// --- переходи живуть ЗЗОВНІ, у різних кутках коду ---

// оформлення (шар оплати)
void payOrder(Order& order) {
    if (order.getStatus() == "new") {
        order.setStatus("paid");
    } else {
        throw std::runtime_error("не можна оплатити: " + order.getStatus());
    }
}

// склад (інший шар, часто інший автор)
void shipOrder(Order& order) {
    // тут ЗАБУЛИ перевірити, що замовлення оплачене
    order.setStatus("shipped");
}

// скасування (ще один шар)
void cancelOrder(Order& order) {
    if (order.getStatus() != "shipped") {
        order.setStatus("cancelled");
    } else {
        throw std::runtime_error("відвантажене вже не скасувати");
    }
}
