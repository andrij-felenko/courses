// Конструктор класу ініціалізує всі необхідні буфери
// Деструктор автоматично звільняє виділені ресурси
class GridLabeler2D {
public:
    explicit GridLabeler2D(
        int width,
        int height,
        Connectivity connectivity = Connectivity::Four,
        BoundaryCondition boundary = BoundaryCondition::Open
    );
    ~GridLabeler2D();

    void reset();
};
