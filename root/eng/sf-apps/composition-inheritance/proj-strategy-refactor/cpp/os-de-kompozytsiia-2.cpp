class Enemy {
    std::unique_ptr<Weapon>  weapon;
    std::unique_ptr<Armor>   armor;
    std::unique_ptr<Element> element;    // ← нове поле
public:
    Enemy(std::unique_ptr<Weapon> w, std::unique_ptr<Armor> a,
          std::unique_ptr<Element> e)
        : weapon(std::move(w)), armor(std::move(a)), element(std::move(e)) {}

    // атака тепер = базова шкода зброї + бонус стихії
    int attack() const { return weapon->hit() + element->bonus(); }
    int defend() const { return armor->block(); }
};
