struct LineDto {
    std::string sku;                // тут уже голий рядок — DTO «дурний»
    int         qty;
    double      unitPrice;          // гроші як double — на межі так буває
};

struct OrderDto {
    long                    id;
    double                  total;  // готовий результат, не собівартість
    std::string             status; // "new" / "paid" / "shipped" / "cancelled"
    std::vector<LineDto>    lines;
};
