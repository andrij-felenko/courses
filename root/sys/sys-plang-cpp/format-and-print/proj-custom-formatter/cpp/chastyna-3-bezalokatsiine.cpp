template <std::size_t BufferSize>
class FastLogger {
public:
    template <typename... Args>
    static void log(std::format_string<Args...> fmt, Args&&... args) {
        // Локальний стековий масив — 0 алокацій у купі!
        alignas(std::max_align_t) std::array<char, BufferSize> buf;

        try {
            // Форматуємо прямо у стековий буфер із суворим обмеженням BufferSize - 1
            auto res = std::format_to_n(buf.data(), buf.size() - 1, fmt, std::forward<Args>(args)...);

            // Обчислюємо кількість фактично записаних байтів
            std::size_t written = std::min(static_cast<std::size_t>(res.size), BufferSize - 1);
            buf[written] = '\0'; // Гарантуємо нульовий термінатор

            // Створюємо безволодісний погляд для прямоточного виводу
            std::string_view out_view(buf.data(), written);
            std::cout << out_view << "\n";

            if (res.size >= static_cast<std::ptrdiff_t>(BufferSize)) {
                // Текст було безпечно обрізано через брак місця у стеку
                std::cerr << "[WARNING]: Log record truncated! Required: " 
                          << res.size << " bytes, available buffer: " << BufferSize - 1 << "\n";
            }
        } catch (const std::format_error& e) {
            std::cerr << "[LOG ERROR]: Exception during formatting: " << e.what() << "\n";
        }
    }
};
