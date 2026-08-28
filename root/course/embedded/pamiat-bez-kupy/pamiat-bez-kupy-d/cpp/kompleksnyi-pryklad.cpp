/* Приклад використання конвеєра обробки на ідіоматичному C++20 */

struct ClientSession {
    std::uint32_t session_id{0};
    std::uint32_t last_active_ms{0};
    std::byte encryption_key[32]{};
};

class TelemetryNode {
public:
    TelemetryNode() = default;

    bool process_frame(std::span<const std::byte> raw_payload) noexcept {
        /* RAII-контроль арени: при будь-якому виході з функції арена відкочується */
        auto frame_scope = frame_arena_.make_scope();

        /* Виділення тимчасових структур для обробки кадру */
        auto decrypted_span = frame_arena_.create_span<std::byte>(raw_payload.size());
        if (decrypted_span.empty() && !raw_payload.empty()) {
            return false; /* Переповнення робочої арени */
        }
        std::ranges::copy(raw_payload, decrypted_span.begin());

        /* Якщо потрібна постійна сесія — виділяємо довготривалий об'єкт через RAII UniquePtr */
        if (raw_payload.size() > 0 && raw_payload[0] == std::byte{0x01}) {
            auto session_ptr = session_pool_.make_unique();
            if (!session_ptr) {
                return false; /* Ліміт сесій вичерпано */
            }
            session_ptr->session_id = 1001;
            session_ptr->last_active_ms = 12000;
            std::ranges::copy(decrypted_span.subspan(0, 32), session_ptr->encryption_key);

            /* Збереження у масив активних з'єднань (передача володіння через move) */
            active_session_ = std::move(session_ptr);
        }

        return true;
    }

    [[nodiscard]] std::size_t get_arena_peak() const noexcept {
        return frame_arena_.peak_bytes();
    }

private:
    FixedPool<ClientSession, 8> session_pool_;
    MemoryArena<1024> frame_arena_;
    FixedPool<ClientSession, 8>::UniquePtr active_session_{nullptr, {nullptr}};
};
