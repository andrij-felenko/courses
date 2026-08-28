namespace crypto::glv {

struct CurveConfig2D {
    std::string_view curve_name;            // Текстовий ідентифікатор кривої
    std::array<uint64_t, 4> p{};            // Просте число модуля поля F_p
    std::array<uint64_t, 4> r{};            // Порядок підгрупи точок кривої r
    std::array<uint64_t, 4> beta{};         // Кубічний корінь з одиниці у полі F_p
    std::array<uint64_t, 4> lambda{};       // Власне значення ендоморфізму
    
    std::array<uint64_t, 2> b11{};          // Елемент b11 короткого базису
    std::array<uint64_t, 2> b12{};          // Елемент b12 короткого базису
    std::array<uint64_t, 2> b21{};          // Елемент b21 короткого базису
    std::array<uint64_t, 2> b22{};          // Елемент b22 короткого базису
    
    std::array<uint64_t, 4> g1{};           // Константа масштабування g1
    std::array<uint64_t, 4> g2{};           // Константа масштабування g2
    uint16_t fixed_shift{384};              // Величина побітового зсуву
};

} // namespace crypto::glv
