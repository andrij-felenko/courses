#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <cstdint>
#include <cstring>
#include <stdexcept>

// Перелік станів кінцевого автомата завантажувача
enum class UploadState {
    Idle,
    SendingCount,
    WaitingRequest,
    WaitingAck,
    Completed,
    Failed
};

// Структура навігаційного пункту місії
struct MissionItem {
    uint16_t seq{0};
    uint16_t command{16}; // MAV_CMD_NAV_WAYPOINT (16)
    uint8_t frame{6};     // MAV_FRAME_GLOBAL_RELATIVE_ALT_INT (6)
    float param1{0.0f};   // Час зависання (Hold time), с
    float param2{2.0f};   // Радіус прийняття точки, м
    float param3{0.0f};   // Проліт через точку (Pass radius)
    float param4{0.0f};   // Бажаний курс (Yaw angle), град
    int32_t latitude_e7{0};  // Широта * 10^7
    int32_t longitude_e7{0}; // Довгота * 10^7
    float altitude{10.0f};   // Висота відносно точки старту, м
    bool autocontinue{true};
};

// Клас транзакційного завантажувача місії
class MissionUploader {
public:
    MissionUploader(uint8_t target_sys, uint8_t target_comp, 
                    std::chrono::milliseconds timeout = std::chrono::milliseconds(500),
                    uint32_t max_retries = 5)
        : target_system_(target_sys),
          target_component_(target_comp),
          timeout_duration_(timeout),
          max_retries_(max_retries),
          state_(UploadState::Idle) {}

    // Ініціалізація нової транзакції завантаження списку пунктів
    void startUpload(const std::vector<MissionItem>& items) {
        if (items.empty()) {
            throw std::invalid_argument("Список місії не може бути порожнім.");
        }
        mission_items_ = items;
        current_seq_ = 0;
        retry_count_ = 0;
        state_ = UploadState::SendingCount;

        // Оголошуємо кількість пунктів автопілоту
        sendMissionCount(static_cast<uint16_t>(mission_items_.size()));
        last_action_time_ = std::chrono::steady_clock::now();
        std::cout << "[FSM] Старт транзакції: оголошено " << mission_items_.size() << " пунктів.\n";
    }

    // Обробка вхідного повідомлення MISSION_REQUEST_INT від автопілота
    void handleMissionRequestInt(uint16_t requested_seq) {
        if (state_ != UploadState::SendingCount && state_ != UploadState::WaitingRequest) {
            std::cout << "[FSM] Отримано неочікуваний запит seq=" << requested_seq << " у неактивному стані.\n";
            return;
        }

        if (requested_seq >= mission_items_.size()) {
            std::cerr << "[FSM] Помилка: автопілот запросив seq=" << requested_seq 
                      << ", що перевищує розмір місії (" << mission_items_.size() << ").\n";
            state_ = UploadState::Failed;
            return;
        }

        // Автопілот запросив черговий або повторний пункт
        current_seq_ = requested_seq;
        retry_count_ = 0; // Успішний рух скидає лічильник повторів

        sendMissionItem(mission_items_[current_seq_]);
        last_action_time_ = std::chrono::steady_clock::now();

        // Якщо це останній пункт — переходимо до очікування фінального ACK
        if (current_seq_ + 1 == mission_items_.size()) {
            state_ = UploadState::WaitingAck;
            std::cout << "[FSM] Передано фінальний пункт seq=" << current_seq_ << ". Очікування ACK...\n";
        } else {
            state_ = UploadState::WaitingRequest;
            std::cout << "[FSM] Надіслано пункт seq=" << current_seq_ << ". Очікування наступного запиту...\n";
        }
    }

    // Обробка фінального повідомлення MISSION_ACK
    void handleMissionAck(uint8_t result_code) {
        if (state_ != UploadState::WaitingAck && state_ != UploadState::WaitingRequest) {
            return;
        }

        if (result_code == 0) { // MAV_MISSION_ACCEPTED
            state_ = UploadState::Completed;
            std::cout << "[FSM] УСПІХ: Місію зафіксовано у Flash автопілота (MAV_MISSION_ACCEPTED).\n";
        } else {
            state_ = UploadState::Failed;
            std::cerr << "[FSM] ПОМИЛКА: Автопілот відхилив місію з кодом помилки: " 
                      << static_cast<int>(result_code) << "\n";
        }
    }

    // Періодична функція оновлення таймерів (має викликатися у головному циклі програми)
    void update(std::chrono::steady_clock::time_point now) {
        if (state_ == UploadState::Idle || state_ == UploadState::Completed || state_ == UploadState::Failed) {
            return;
        }

        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_action_time_);
        if (elapsed > timeout_duration_) {
            if (retry_count_ >= max_retries_) {
                std::cerr << "[FSM] ТАЙМАУТ: Перевищено ліміт спроб (" << max_retries_ 
                          << "). Транзакцію скасовано.\n";
                state_ = UploadState::Failed;
                return;
            }

            retry_count_++;
            std::cout << "[FSM] Таймаут відповіді. Повторна спроба " << retry_count_ 
                      << " з " << max_retries_ << "...\n";

            if (state_ == UploadState::SendingCount) {
                sendMissionCount(static_cast<uint16_t>(mission_items_.size()));
            } else if (state_ == UploadState::WaitingRequest || state_ == UploadState::WaitingAck) {
                sendMissionItem(mission_items_[current_seq_]);
            }
            last_action_time_ = now;
        }
    }

    UploadState getState() const { return state_; }

private:
    void sendMissionCount(uint16_t count) {
        // У реальній системі тут викликається mavlink_msg_mission_count_pack() та відправка у UART/UDP
        std::cout << "  -> TX: MISSION_COUNT (count=" << count 
                  << ", target_sys=" << static_cast<int>(target_system_) << ")\n";
    }

    void sendMissionItem(const MissionItem& item) {
        // У реальній системі тут викликається mavlink_msg_mission_item_int_pack()
        std::cout << "  -> TX: MISSION_ITEM_INT (seq=" << item.seq 
                  << ", cmd=" << item.command << ", lat=" << item.latitude_e7 
                  << ", lon=" << item.longitude_e7 << ", alt=" << item.altitude << "m)\n";
    }

    uint8_t target_system_;
    uint8_t target_component_;
    std::chrono::milliseconds timeout_duration_;
    uint32_t max_retries_;

    UploadState state_;
    std::vector<MissionItem> mission_items_;
    uint16_t current_seq_{0};
    uint32_t retry_count_{0};
    std::chrono::steady_clock::time_point last_action_time_;
};
