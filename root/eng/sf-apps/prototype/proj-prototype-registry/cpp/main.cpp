#include <memory>
#include <string>
#include <vector>

struct Entity {
    virtual ~Entity() = default;
    // «віртуальний конструктор»: кожен нащадок віддасть копію СВОГО типу
    virtual std::unique_ptr<Entity> clone() const = 0;
    virtual void render() const = 0;
};

struct Monster : Entity {
    std::string name;
    int hp;
    std::vector<std::string> loot;      // ВЛАСНИЙ вектор

    Monster(std::string name, int hp, std::vector<std::string> loot)
        : name(std::move(name)), hp(hp), loot(std::move(loot)) {}

    std::unique_ptr<Entity> clone() const override {
        // одне тіло — виклик КОНСТРУКТОРА КОПІЇ через *this
        return std::make_unique<Monster>(*this);   // Monster(const Monster&)
    }
    void render() const override { /* намалювати */ }
};
