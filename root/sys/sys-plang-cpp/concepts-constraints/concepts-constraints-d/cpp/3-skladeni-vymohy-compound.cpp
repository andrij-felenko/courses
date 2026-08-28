template<typename T>
concept SmartHandle = requires(T handle) {
    // 1. Метод close() існує, не викидає винятків і повертає void
    { handle.close() } noexcept -> std::same_as<void>;

    // 2. Метод size() існує і повертає тип, що задовольняє std::integral
    { handle.size() } -> std::integral;

    // 3. Розіменування повертає посилання, що конвертується в const char*
    { *handle } -> std::convertible_to<const char*>;
};
