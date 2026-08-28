// Усередині — багатий домен з поведінкою і прихованими полями
class Order {
    OrderId   id_;            // внутрішній ключ бази — назовні не потрібен
    Money     cost_;          // собівартість — комерційна таємниця
    std::vector<Line> lines_;
    Status    status_;
public:
    Money total() const;             // правило: як рахується сума
    void  cancel();                  // правило: коли можна скасувати
    // ... інваріанти, що бережуть коректність
};

// На межі — пласка виписка: лише те, що клієнт має право й потребу бачити
struct OrderDto {
    long        id;
    double      total;               // порахований результат, не собівартість
    std::string status;
    std::vector<LineDto> lines;
};
