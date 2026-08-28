#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <system_error>

namespace fs = std::filesystem;

enum class MessageType : uint8_t {
    Prepare = 1,
    VoteCommit = 2,
    VoteAbort = 3,
    GlobalCommit = 4,
    GlobalAbort = 5,
    Ack = 6
};

enum class TxState : uint8_t {
    Init = 0,
    Preparing = 1,
    Prepared = 2, // In-Doubt
    Committed = 3,
    Aborted = 4,
    Done = 5
};

struct WalRecord {
    uint32_t magic{0x3250434Du};
    uint32_t tx_id{0};
    TxState state{TxState::Init};
    uint32_t crc{0};
};

class DurableWal {
public:
    explicit DurableWal(std::string_view path) : path_(path) {
        stream_.open(path_, std::ios::binary | std::ios::out | std::ios::app);
        if (!stream_.is_open()) {
            throw std::runtime_error("Не вдалося відкрити журнал WAL: " + path_);
        }
    }

    ~DurableWal() {
        if (stream_.is_open()) {
            stream_.flush();
            stream_.close();
        }
    }

    void write_state(uint32_t tx_id, TxState state) {
        WalRecord record{
            .magic = 0x3250434Du,
            .tx_id = tx_id,
            .state = state,
            .crc = tx_id ^ static_cast<uint32_t>(state)
        };
        stream_.write(reinterpret_cast<const char*>(&record), sizeof(record));
        stream_.flush(); // Гарантоване скидання буферів
    }

    [[nodiscard]] std::string_view path() const noexcept { return path_; }

private:
    std::string path_;
    std::ofstream stream_;
};

class Participant {
public:
    Participant(int id, bool crash_injection = false)
        : id_(id),
          crash_injection_(crash_injection),
          wal_("participant_" + std::to_string(id) + ".wal") {}

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] TxState state() const noexcept { return state_; }
    void set_crash_injection(bool enable) noexcept { crash_injection_ = enable; }

    MessageType handle_message(uint32_t tx_id, MessageType msg) {
        switch (msg) {
            case MessageType::Prepare: {
                std::cout << "  [Вузол " << id_ << "] Отримано PREPARE для TX=" << tx_id << "\n";
                wal_.write_state(tx_id, TxState::Prepared);
                state_ = TxState::Prepared;
                std::cout << "  [Вузол " << id_ << "] Зафіксовано стан PREPARED у WAL (In-Doubt).\n";

                if (crash_injection_) {
                    std::cout << "  [Вузол " << id_ << "] 💥 Відмова вузла під час голосування!\n";
                    return MessageType::VoteAbort;
                }
                return MessageType::VoteCommit;
            }
            case MessageType::GlobalCommit: {
                std::cout << "  [Вузол " << id_ << "] Отримано GLOBAL_COMMIT. Фіксація даних.\n";
                wal_.write_state(tx_id, TxState::Committed);
                state_ = TxState::Committed;
                return MessageType::Ack;
            }
            case MessageType::GlobalAbort: {
                std::cout << "  [Вузол " << id_ << "] Отримано GLOBAL_ABORT. Відкат даних.\n";
                wal_.write_state(tx_id, TxState::Aborted);
                state_ = TxState::Aborted;
                return MessageType::Ack;
            }
            default:
                return MessageType::VoteAbort;
        }
    }

    void cleanup_wal() {
        std::error_code ec;
        fs::remove(wal_.path(), ec);
    }

private:
    int id_;
    bool crash_injection_{false};
    TxState state_{TxState::Init};
    DurableWal wal_;
};

class Coordinator {
public:
    Coordinator() : wal_("coordinator.wal") {}

    void register_participant(std::shared_ptr<Participant> p) {
        participants_.push_back(std::move(p));
    }

    std::expected<bool, std::string> execute_transaction(uint32_t tx_id) {
        std::cout << "[Координатор] Старт розподіленої транзакції TX=" << tx_id << "\n";

        // Фаза 1: Голосування (Prepare)
        wal_.write_state(tx_id, TxState::Preparing);
        state_ = TxState::Preparing;
        std::cout << "[Координатор] Фаза 1: надсилання PREPARE до " << participants_.size() << " учасників\n";

        bool all_voted_yes = true;
        for (const auto& p : participants_) {
            auto vote = p->handle_message(tx_id, MessageType::Prepare);
            if (vote == MessageType::VoteCommit) {
                std::cout << "[Координатор] Вузол " << p->id() << " проголосував VOTE_COMMIT\n";
            } else {
                std::cout << "[Координатор] Вузол " << p->id() << " проголосував VOTE_ABORT\n";
                all_voted_yes = false;
            }
        }

        // Фаза 2: Ухвалення рішення
        if (all_voted_yes) {
            std::cout << "[Координатор] Усі голоси ствердні. Рішення: GLOBAL_COMMIT\n";
            wal_.write_state(tx_id, TxState::Committed);
            state_ = TxState::Committed;

            for (const auto& p : participants_) {
                auto ack = p->handle_message(tx_id, MessageType::GlobalCommit);
                if (ack == MessageType::Ack) {
                    std::cout << "[Координатор] Підтвердження (ACK) від вузла " << p->id() << "\n";
                }
            }
        } else {
            std::cout << "[Координатор] Виявлено відмову. Рішення: GLOBAL_ABORT\n";
            wal_.write_state(tx_id, TxState::Aborted);
            state_ = TxState::Aborted;

            for (const auto& p : participants_) {
                p->handle_message(tx_id, MessageType::GlobalAbort);
            }
        }

        wal_.write_state(tx_id, TxState::Done);
        state_ = TxState::Done;
        std::cout << "[Координатор] Транзакцію TX=" << tx_id << " завершено.\n\n";

        return all_voted_yes;
    }

    void cleanup_wal() {
        std::error_code ec;
        fs::remove(wal_.path(), ec);
    }

private:
    TxState state_{TxState::Init};
    DurableWal wal_;
    std::vector<std::shared_ptr<Participant>> participants_;
};

int main() {
    try {
        Coordinator coordinator;
        auto p1 = std::make_shared<Participant>(1, false);
        auto p2 = std::make_shared<Participant>(2, false);

        coordinator.register_participant(p1);
        coordinator.register_participant(p2);

        // Тест 1: Успішне виконання
        auto res1 = coordinator.execute_transaction(2001);

        // Тест 2: Відкат через збій другого учасника
        p2->set_crash_injection(true);
        auto res2 = coordinator.execute_transaction(2002);

        // Прибирання журналів
        coordinator.cleanup_wal();
        p1->cleanup_wal();
        p2->cleanup_wal();
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
