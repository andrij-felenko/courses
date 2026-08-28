#include <string>
#include <vector>
#include <memory>

struct Component {
    std::string name;
    explicit Component(std::string n) : name(std::move(n)) {}
    virtual ~Component() = default;              // робить тип поліморфним → доступний dynamic_cast
};

struct File : Component {
    long bytes;
    File(std::string n, long b) : Component(std::move(n)), bytes(b) {}
};

struct Folder : Component {
    std::vector<std::unique_ptr<Component>> children;   // тека ВОЛОДІЄ дітьми
    explicit Folder(std::string n) : Component(std::move(n)) {}

    Folder* add(std::unique_ptr<Component> c) {
        children.push_back(std::move(c));
        return this;                             // зручно ланцюжком будувати дерево
    }
};

// піддослідне дерево (будова — у тілі якоїсь функції)
auto ui = std::make_unique<Folder>("ui");
ui->add(std::make_unique<File>("button.ts", 640))
  ->add(std::make_unique<File>("modal.ts", 1500));

auto src = std::make_unique<Folder>("src");
src->add(std::make_unique<File>("main.ts", 1200))
   ->add(std::make_unique<File>("util.ts", 800));
src->add(std::move(ui));

auto docs = std::make_unique<Folder>("docs");
docs->add(std::make_unique<File>("guide.md", 300))
    ->add(std::make_unique<File>("api.md", 950));

auto tree = std::make_unique<Folder>("проєкт");
tree->add(std::move(src));
tree->add(std::move(docs));
tree->add(std::make_unique<File>("README.md", 200));
