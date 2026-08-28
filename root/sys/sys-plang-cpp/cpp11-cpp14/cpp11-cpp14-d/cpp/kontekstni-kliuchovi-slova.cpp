class Base {
public:
    virtual void render(int width, int height) const;
};

class Derived : public Base {
public:
    // Помилка компіляції, якщо випадково пропущено const або змінено тип
    void render(int width, int height) const override;
};
