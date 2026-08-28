struct Shape {
    virtual ~Shape() = default;
    virtual Shape* clone() const = 0;   // «віртуальний конструктор»
};

struct Circle : Shape {
    int x, y, r;
    Circle* clone() const override {    // коваріантний тип повернення
        return new Circle(*this);       // усередині — звичайний конструктор копії
    }
};
