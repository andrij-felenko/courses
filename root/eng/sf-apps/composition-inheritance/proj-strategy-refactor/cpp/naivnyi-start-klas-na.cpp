#include <cstdio>

// Базовий ворог: обіцяє два числа — завдану й поглинуту шкоду.
class Enemy {
public:
    virtual int attack() const = 0;   // скільки шкоди завдає
    virtual int defend() const = 0;   // скільки шкоди тримає
    virtual ~Enemy() = default;
};

// Кожна КОМБІНАЦІЯ зброя×броня — окремий клас.
class SwordLight : public Enemy {
public:
    int attack() const override { return 10; }  // меч
    int defend() const override { return 2;  }   // легка
};
class SwordHeavy : public Enemy {
public:
    int attack() const override { return 10; }  // меч
    int defend() const override { return 7;  }   // важка
};
class BowLight : public Enemy {
public:
    int attack() const override { return 6; }   // лук
    int defend() const override { return 2; }    // легка
};
class BowHeavy : public Enemy {
public:
    int attack() const override { return 6; }   // лук
    int defend() const override { return 7; }    // важка
};
