// example_api.cpp — ідіоматичний C++20 варіант
#include <iostream>
#include <memory>
#include <string_view>
#include <format>
#include <array>
#include <systemd/sd-journal.h>

class JournalAPIWrapper {
    struct JournalCloser {
        void operator()(sd_journal *j) const noexcept {
            if (j) sd_journal_close(j);
        }
    };
    std::unique_ptr<sd_journal, JournalCloser> handle_;

public:
    JournalAPIWrapper() {
        sd_journal *raw = nullptr;
        if (sd_journal_open(&raw, SD_JOURNAL_LOCAL_ONLY) < 0) {
            throw std::runtime_error("Не вдалося відкрити журнал systemd");
        }
        handle_.reset(raw);
    }

    static void send_transaction_log(std::string_view tx_id, uint64_t amount_cent) {
        std::string msg = std::format("MESSAGE=Старт обробки транзакції {}", tx_id);
        std::string prio = std::format("PRIORITY={}", LOG_NOTICE);
        std::string tx = std::format("TRANSACTION_ID={}", tx_id);
        std::string amt = std::format("AMOUNT_CENT={}", amount_cent);

        int r = sd_journal_send(
            msg.c_str(),
            prio.c_str(),
            tx.c_str(),
            amt.c_str(),
            "CURRENCY=UAH",
            nullptr
        );
        if (r < 0) {
            std::cerr << "Помилка відправки логу: " << strerror(-r) << "\n";
        }
    }

    void watch_unit_events(std::string_view unit_name) {
        std::string match = std::format("_SYSTEMD_UNIT={}", unit_name);
        sd_journal_add_match(handle_.get(), match.c_str(), 0);
        sd_journal_seek_tail(handle_.get());

        std::cout << std::format("Моніторинг подій {} через C++ epoll...\n", unit_name);
        for (int i = 0; i < 3; ++i) {
            int r = sd_journal_wait(handle_.get(), 5000000); // 5 sec timeout
            if (r == SD_JOURNAL_NOP) {
                std::cout << "Очікування нових записів...\n";
                continue;
            }

            while (sd_journal_next(handle_.get()) > 0) {
                const void *data = nullptr;
                size_t len = 0;
                if (sd_journal_get_data(handle_.get(), "MESSAGE", &data, &len) >= 0) {
                    std::string_view msg_sv(static_cast<const char*>(data), len);
                    std::cout << std::format("Отримано: {}\n", msg_sv);
                }
            }
        }
    }
};
