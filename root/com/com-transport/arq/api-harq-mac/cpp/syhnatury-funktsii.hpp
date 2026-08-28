#include <cstdint>
#include <span>
#include <expected>
#include <vector>

enum class HarqError : uint8_t {
    InvalidProcessId,
    NoFreeProcess,
    BufferOverflow,
    OutOfSyncNdi,
    MaxRetriesReached
};

class HarqEntity {
public:
    explicit HarqEntity(uint16_t rnti, uint8_t num_processes, uint32_t total_soft_buffer_bytes);

    // Виділення вільного процесу HARQ для передачі нового блоку
    [[nodiscard]] std::expected<uint8_t, HarqError> allocate_tx_process();

    // Підготовка дескриптора передачі
    [[nodiscard]] std::expected<HarqTxProcessDescriptor, HarqError> prepare_tx_pdu(
        uint8_t process_id, bool is_new_data, std::span<const uint8_t> payload, uint32_t tbs);

    // Обробка отриманого зворотного зв'язку від фізичного рівня
    [[nodiscard]] std::expected<void, HarqError> handle_feedback(uint8_t process_id, HarqFeedback feedback);

    // Софт-комбінування та запуск апаратного декодера
    [[nodiscard]] std::expected<bool, HarqError> combine_and_decode(
        uint8_t process_id, bool received_ndi, HarqRedundancyVersion rv,
        std::span<const int8_t> rx_llr, std::span<uint8_t> out_payload);

    // Скидання буфера
    void reset_process(uint8_t process_id);
};
