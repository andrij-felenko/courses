#include "sim/fake_modem.hpp"

#include <algorithm>
#include <charconv>
#include <utility>

namespace sim {
namespace {

[[nodiscard]] bool due_now(at::Millis now, at::Millis due) noexcept
{
    return static_cast<std::int32_t>(now.count() - due.count()) >= 0;
}

}  // namespace

void FakeModem::schedule(std::string text, at::Millis due, std::size_t chunk, at::Millis gap)
{
    outbox_.push_back(Pending{std::move(text), 0, chunk, gap, due});
}

void FakeModem::emit(std::string_view bytes) noexcept
{
    for (const char c : bytes) {
        dma_[head_] = static_cast<std::uint8_t>(c);
        head_ = static_cast<std::uint16_t>((head_ + 1) & at::config::kRxMask);
    }
}

void FakeModem::on_command(at::Millis now)
{
    const std::string_view cmd{rx_line_};
    if (cmd.empty()) {
        return;
    }

    if (echo_) {
        schedule(rx_line_ + "\r\n", now);
    }

    if (cmd == "ATE0") {
        echo_ = false;
        schedule("\r\nOK\r\n", now + at::Millis{10});
        return;
    }

    if (cmd == "AT+CFUN=1") {
        ++cfun_attempts_;
        if (cfun_attempts_ == 1) {
            // Перша спроба впирається в зайняту SIM — тимчасова помилка.
            schedule("\r\n+CME ERROR: 14\r\n", now + at::Millis{30});
        } else {
            // Друга йде довго: підняти радіомодуль справді коштує часу.
            schedule("\r\nOK\r\n", now + at::Millis{250});
        }
        return;
    }

    if (cmd == "AT+CSQ") {
        // Відповідь навмисно рветься посеред рядка: сім байтів, пауза 25 мс,
        // решта. Парсер зобов'язаний дочекатися '\n'.
        schedule("\r\n+CSQ: 24,99\r\n\r\nOK\r\n", now + at::Millis{25}, 7, at::Millis{25});
        return;
    }

    if (cmd.starts_with("AT+QISEND=")) {
        const std::string_view args = cmd.substr(std::string_view{"AT+QISEND="}.size());
        int socket_id = -1;
        std::from_chars(args.data(), args.data() + args.size(), socket_id);

        const auto comma = cmd.find(',', std::string_view{"AT+QISEND="}.size());
        payload_expect_ = 0;
        payload_got_ = 0;

        if (socket_id != 0) {
            // Сокет не відкритий. Модуль відмовляє одразу й запрошення не
            // надсилає ВЗАГАЛІ — це та пастка, на якій зависає драйвер, що в
            // стані очікування '>' дивиться самі лише сирі байти.
            schedule("\r\nERROR\r\n", now + at::Millis{15});
            return;
        }
        if (comma != std::string_view::npos) {
            const std::string_view digits = cmd.substr(comma + 1);
            std::from_chars(digits.data(), digits.data() + digits.size(), payload_expect_);
        }
        if (payload_expect_ > 0) {
            await_payload_ = true;
            schedule("\r\n> ", now + at::Millis{15});
        } else {
            schedule("\r\nERROR\r\n", now + at::Millis{15});
        }
        return;
    }

    if (cmd.starts_with("AT+QIOPEN")) {
        schedule("\r\nOK\r\n", now + at::Millis{20});
        // Результат відкриття сокета приходить окремим URC — значно пізніше за
        // "OK", і саме тому його не можна чекати в контексті команди.
        schedule("\r\n+QIOPEN: 0,0\r\n", now + at::Millis{120});
        return;
    }

    if (cmd.starts_with("AT+QIDEACT")) {
        // Мовчанка: так поводиться модуль із завислим внутрішнім стеком.
        return;
    }

    schedule("\r\nOK\r\n", now + at::Millis{20});
}

void FakeModem::on_tx(std::span<const std::byte> data, at::Millis now)
{
    for (const std::byte raw : data) {
        const char c = static_cast<char>(raw);

        if (await_payload_) {
            // Сирі байти можуть містити і '\r', і '\n' — рахуємо їх за
            // довжиною, оголошеною в команді, а не за термінатором.
            ++payload_got_;
            if (payload_got_ >= payload_expect_) {
                await_payload_ = false;
                schedule("\r\nSEND OK\r\n", now + at::Millis{40});
            }
            continue;
        }

        if (c == '\n') {
            on_command(now);
            rx_line_.clear();
            continue;
        }
        if (c == '\r') {
            continue;
        }
        rx_line_.push_back(c);
    }
}

void FakeModem::tick(at::Millis now)
{
    // Спонтанні події, яких ніхто не замовляв.
    if (!urc_closed_done_ && now >= at::Millis{900}) {
        urc_closed_done_ = true;
        // Розрив сокета приходить двома кадрами: "+QIURC: \"clo" і решта через
        // 20 мс. Наївний парсер тут розірве повідомлення навпіл.
        schedule("\r\n+QIURC: \"closed\",0\r\n", now, 12, at::Millis{20});
    }
    if (!urc_ring_done_ && now >= at::Millis{1500}) {
        urc_ring_done_ = true;
        schedule("\r\nRING\r\n", now);
    }

    // Видача запланованого. Порядок суворо FIFO: дріт один.
    while (!outbox_.empty()) {
        Pending& front = outbox_.front();
        if (!due_now(now, front.due)) {
            break;
        }

        const std::size_t remain = front.text.size() - front.sent;
        const std::size_t take = (front.chunk > 0 && front.chunk < remain) ? front.chunk : remain;

        emit(std::string_view{front.text}.substr(front.sent, take));
        front.sent += take;

        if (front.sent >= front.text.size()) {
            outbox_.pop_front();
            continue;
        }

        front.due = now + front.gap;
        break;
    }
}

}  // namespace sim
