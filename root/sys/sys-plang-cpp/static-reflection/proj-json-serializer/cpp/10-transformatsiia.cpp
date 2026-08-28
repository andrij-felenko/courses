template <typename StructType>
class SoAContainer {
    // Автоматичне обчислення типів векторів для кожного поля StructType
    static consteval auto generate_soa_layout() -> std::meta::info {
        std::vector<std::meta::data_member_spec> specs;
        for (auto f : std::meta::nonstatic_data_members_of(^^StructType)) {
            auto vec_type = std::meta::substitute(^^std::vector, std::array{std::meta::type_of(f)});
            specs.push_back({
                .type = vec_type,
                .name = std::meta::name_of(f)
            });
        }
        return std::meta::define_class(specs);
    }

    using Storage = [: generate_soa_layout() :];
    Storage storage;
    size_t count = 0;

public:
    void push_back(const StructType& item) {
        template for (constexpr auto f : std::meta::nonstatic_data_members_of(^^StructType)) {
            constexpr auto member_name = std::meta::name_of(f);
            // Додаємо елемент у відповідний вектор SoA-сховища
            storage.[: f :].push_back(item.[: f :]);
        }
        count++;
    }

    auto size() const noexcept -> size_t { return count; }
};
