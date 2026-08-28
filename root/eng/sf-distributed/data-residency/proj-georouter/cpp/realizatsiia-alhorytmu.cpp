namespace georouter {

class Tokenizer {
public:
    static std::string generate_token(std::string_view input, std::string_view salt) noexcept {
        constexpr uint64_t FNV_OFFSET_BASIS = 0xcbf29ce484222325ULL;
        constexpr uint64_t FNV_PRIME = 0x100000001b3ULL;

        uint64_t hash = FNV_OFFSET_BASIS;
        for (char ch : salt) {
            hash ^= static_cast<uint8_t>(ch);
            hash *= FNV_PRIME;
        }
        for (char ch : input) {
            hash ^= static_cast<uint8_t>(ch);
            hash *= FNV_PRIME;
        }

        char buffer[32];
        std::snprintf(buffer, sizeof(buffer), "tok_%016llx", static_cast<unsigned long long>(hash));
        return std::string(buffer);
    }
};

} // namespace georouter
