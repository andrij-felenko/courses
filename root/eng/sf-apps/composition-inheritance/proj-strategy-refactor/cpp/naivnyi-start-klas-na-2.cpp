// Додаємо ОДНУ броню — а класів доводиться дописати стільки,
// скільки є видів зброї:
class SwordMagic : public Enemy {
public:
    int attack() const override { return 10; }
    int defend() const override { return 5; }
};
class BowMagic : public Enemy {
public:
    int attack() const override { return 6; }
    int defend() const override { return 5; }
};
// Було 4 → стало 6. Одна нова броня коштувала ДВА класи.
