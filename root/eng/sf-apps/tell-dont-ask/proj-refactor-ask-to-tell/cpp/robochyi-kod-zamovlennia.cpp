#include <string>
#include <stdexcept>

enum class Status { New, Paid, Shipped, Cancelled };

// для повідомлень і показу — стан у людський рядок
std::string toString(Status s) {
    switch (s) {
        case Status::New:       return "new";
        case Status::Paid:      return "paid";
        case Status::Shipped:   return "shipped";
        case Status::Cancelled: return "cancelled";
    }
    return "?";
}

// власний тип помилки — щоб викликач ловив саме недозволений перехід
class OrderError : public std::logic_error {
public:
    explicit OrderError(const std::string& msg) : std::logic_error(msg) {}
};

class Order {
public:
    explicit Order(std::string id)
        : id_(std::move(id)), status_(Status::New) {}

    // --- КОМАНДИ: кожна стереже свій інваріант ---

    void pay() {
        require(status_ == Status::New, "оплатити можна лише нове");
        status_ = Status::Paid;
    }

    void ship() {
        require(status_ == Status::Paid, "відвантажити можна лише оплачене");
        status_ = Status::Shipped;
    }

    void cancel() {
        require(status_ != Status::Shipped && status_ != Status::Cancelled,
                "скасувати вже не можна");
        status_ = Status::Cancelled;
    }

    // --- ЗАПИТ: лише читає, нічого не міняє ---
    Status status() const { return status_; }
    const std::string& id() const { return id_; }

private:
    // спільний вартовий: не виконуй перехід, якщо умова хибна
    void require(bool ok, const char* why) const {
        if (!ok)
            throw OrderError(std::string(why) + " (зараз " + toString(status_) + ")");
    }

    std::string id_;
    Status status_;
};
