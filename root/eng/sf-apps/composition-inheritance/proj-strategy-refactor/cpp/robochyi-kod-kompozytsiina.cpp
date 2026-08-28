#include <cstdio>
#include <memory>
#include <utility>

// ── Вісь «зброя»: інтерфейс + різновиди (по одному класу на вид) ──
struct Weapon {
    virtual int  hit()  const = 0;      // скільки шкоди завдає
    virtual const char* name() const = 0;
    virtual ~Weapon() = default;
};
struct Sword : Weapon {
    int hit() const override { return 10; }       // логіка меча — В ОДНОМУ місці
    const char* name() const override { return "меч"; }
};
struct Bow : Weapon {
    int hit() const override { return 6; }
    const char* name() const override { return "лук"; }
};

// ── Вісь «броня»: інтерфейс + різновиди ──
struct Armor {
    virtual int  block() const = 0;     // скільки шкоди тримає
    virtual const char* name() const = 0;
    virtual ~Armor() = default;
};
struct Light : Armor {
    int block() const override { return 2; }
    const char* name() const override { return "легка"; }
};
struct Heavy : Armor {
    int block() const override { return 7; }
    const char* name() const override { return "важка"; }
};
struct Magic : Armor {
    int block() const override { return 5; }
    const char* name() const override { return "магічна"; }
};

// ── Ворог НЕ успадковує осі — він їх ТРИМАЄ полями ──
class Enemy {
    std::unique_ptr<Weapon> weapon;     // яка зброя зараз
    std::unique_ptr<Armor>  armor;      // яка броня зараз
public:
    Enemy(std::unique_ptr<Weapon> w, std::unique_ptr<Armor> a)
        : weapon(std::move(w)), armor(std::move(a)) {}

    // Делегувальні обгортки: ворог не рахує сам, а перепитує деталь.
    int attack() const { return weapon->hit();  }
    int defend() const { return armor->block(); }

    void describe() const {
        std::printf("ворог: %s + %s → атака %d, захист %d\n",
                    weapon->name(), armor->name(), attack(), defend());
    }
};
