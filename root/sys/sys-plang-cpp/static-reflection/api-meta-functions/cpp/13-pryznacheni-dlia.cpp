namespace std::meta {
    // Отримання списку дескрипторів усіх анотацій, прикріплених до сутності
    consteval auto annotations_of(info entity) -> std::vector<info>;

    // Перевірка наявності анотації заданого типу
    template <typename AnnotationType>
    consteval auto has_annotation(info entity) -> bool;

    // Вилучення екземпляра анотації заданого типу
    template <typename AnnotationType>
    consteval auto get_annotation(info entity) -> std::optional<AnnotationType>;
}
