class Enemy {
    std::unique_ptr<Weapon> weapon;
    std::unique_ptr<Armor>  armor;
public:
    Enemy(std::unique_ptr<Weapon> w, std::unique_ptr<Armor> a)
        : weapon(std::move(w)), armor(std::move(a)) {}

    int attack() const { return weapon->hit(); }
    int defend() const { return armor->block(); }

    // Підміна стратегії НА ЛЬОТУ — той самий об'єкт, інша поведінка.
    void rearm(std::unique_ptr<Weapon> w) { weapon = std::move(w); }
};

int main() {
    Enemy foe(std::make_unique<Sword>(), std::make_unique<Heavy>());
    std::printf("до: атака %d\n", foe.attack());   // до: атака 10

    foe.rearm(std::make_unique<Bow>());            // меч зламався — беремо лук
    std::printf("після: атака %d\n", foe.attack()); // після: атака 6
    return 0;
}
