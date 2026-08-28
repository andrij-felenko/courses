// Кожна вісь — окремий інтерфейс поведінки
struct Weapon { virtual int  hit()   const = 0; virtual ~Weapon() = default; };
struct Armor  { virtual int  block() const = 0; virtual ~Armor()  = default; };

struct Sword : Weapon { int hit()   const override { return 10; } };
struct Bow   : Weapon { int hit()   const override { return 6;  } };
struct Light : Armor  { int block() const override { return 2;  } };
struct Heavy : Armor  { int block() const override { return 7;  } };

// Ворог НЕ успадковує зброю чи броню — він їх ТРИМАЄ
class Enemy {
    std::unique_ptr<Weapon> weapon;
    std::unique_ptr<Armor>  armor;
public:
    Enemy(std::unique_ptr<Weapon> w, std::unique_ptr<Armor> a)
        : weapon(std::move(w)), armor(std::move(a)) {}
    int attack() const { return weapon->hit(); }
    int defend() const { return armor->block(); }
};

// Будь-яку комбінацію збирають на місці — нового класу не треба
Enemy archer(std::make_unique<Bow>(), std::make_unique<Heavy>());
