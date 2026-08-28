// journal_reader.cpp — ідіоматична реалізація на C++20/C++23
#include <iostream>
#include <memory>
#include <string_view>
#include <expected>
#include <system_error>
#include <format>
#include <systemd/sd-journal.h>

class JournalSession {
    struct JournalDeleter {
        void operator()(sd_journal *j) const noexcept {
            if (j) sd_journal_close(j);
        }
    };
    std::unique_ptr<sd_journal, JournalDeleter> handle_;

public:
    static std::expected<JournalSession, std::error_code> create(int flags = SD_JOURNAL_LOCAL_ONLY) {
        sd_journal *raw = nullptr;
        int r = sd_journal_open(&raw, flags);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }
        return JournalSession(raw);
    }

    explicit JournalSession(sd_journal *raw) noexcept : handle_(raw) {}

    std::error_code filter_by_unit(std::string_view unit_name) {
        std::string match = std::format("_SYSTEMD_UNIT={}", unit_name);
        int r = sd_journal_add_match(handle_.get(), match.c_str(), 0);
        if (r < 0) {
            return std::make_error_code(static_cast<std::errc>(-r));
        }
        return {};
    }

    std::expected<std::string_view, std::error_code> get_field(std::string_view field_name) {
        const void *data = nullptr;
        size_t len = 0;
        int r = sd_journal_get_data(handle_.get(), std::string(field_name).c_str(), &data, &len);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }

        std::string_view raw_str(static_cast<const char*>(data), len);
        auto eq_pos = raw_str.find('=');
        if (eq_pos != std::string_view::npos) {
            return raw_str.substr(eq_pos + 1);
        }
        return raw_str;
    }

    std::expected<std::string, std::error_code> get_cursor() {
        char *c_str = nullptr;
        int r = sd_journal_get_cursor(handle_.get(), &c_str);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }
        std::string res(c_str);
        free(c_str);
        return res;
    }

    bool seek_tail() {
        return sd_journal_seek_tail(handle_.get()) >= 0;
    }

    bool previous() {
        return sd_journal_previous(handle_.get()) > 0;
    }
};

int main(int argc, char *argv[]) {
    std::string_view unit = (argc > 1) ? argv[1] : "sshd.service";

    auto session_res = JournalSession::create();
    if (!session_res) {
        std::cerr << "Помилка відкриття журналу: " << session_res.error().message() << "\n";
        return 1;
    }

    auto &session = *session_res;
    if (auto err = session.filter_by_unit(unit); err) {
        std::cerr << "Помилка фільтрації: " << err.message() << "\n";
        return 1;
    }

    if (!session.seek_tail()) {
        std::cerr << "Не вдалося перейти в кінець журналу\n";
        return 1;
    }

    std::cout << std::format("=== Читання логів {} через C++ RAII ===\n", unit);

    int count = 0;
    while (session.previous() && count < 5) {
        count++;
        std::cout << std::format("\nЗапис #{}:\n", count);

        for (auto field : {"_SYSTEMD_UNIT", "_PID", "_UID", "PRIORITY", "MESSAGE"}) {
            if (auto val = session.get_field(field); val) {
                std::cout << std::format("  {}: {}\n", field, *val);
            } else {
                std::cout << std::format("  {}: <відсутнє>\n", field);
            }
        }

        if (auto cursor = session.get_cursor(); cursor) {
            std::cout << std::format("  Cursor: {}\n", *cursor);
        }
    }

    return 0;
}
