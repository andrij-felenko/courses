#include <meta>
#include <memory>
#include <utility>

class AnyDrawable {
    struct Concept {
        virtual ~Concept() = default;
        virtual void draw_virtual() const = 0;
    };

    template <typename T>
    struct Model final : Concept {
        T object;
        Model(T obj) : object(std::move(obj)) {}
        void draw_virtual() const override {
            // Компілятор інспектує наявність методу draw() через рефлексію
            constexpr auto has_draw = [] consteval {
                for (auto member : std::meta::members_of(^^T)) {
                    if (std::meta::name_of(member) == "draw" && std::meta::is_function(member)) {
                        return true;
                    }
                }
                return false;
            }();

            static_assert(has_draw, "Об'єкт повинен мати метод draw()!");
            object.draw();
        }
    };

    std::unique_ptr<Concept> ptr_;

public:
    template <typename T>
    AnyDrawable(T obj) : ptr_(std::make_unique<Model<T>>(std::move(obj))) {}

    void draw() const {
        ptr_->draw_virtual();
    }
};

struct Circle { void draw() const { std::cout << "Circle::draw\n"; } };
struct Square { void draw() const { std::cout << "Square::draw\n"; } };

void test_type_erasure() {
    std::vector<AnyDrawable> shapes;
    shapes.push_back(Circle{});
    shapes.push_back(Square{});

    for (const auto& s : shapes) {
        s.draw();
    }
}
