#include "dispatcher.hpp"

#include <algorithm>
#include <format>
#include <iostream>
#include <ranges>

namespace cmdctl {

void Dispatcher::emit(std::uint8_t phase, const Record& record) {
    const Ack ack{record.token, phase, record.state, record.result, record.detail};
    sink_.send(encode_ack(ack).view());
}

Dispatcher::Record* Dispatcher::find(std::uint64_t token) noexcept {
    auto it = std::ranges::find_if(ring_, [token](const Record& r) {
        return r.state != State::Free && r.token == token;
    });
    return (it != ring_.end()) ? &*it : nullptr;
}

// Витіснення найстарішого слота. Слоти незавершених команд пропускаємо: на них
// посилається черга виконання, і затерти такий слот означало б загубити
// команду посеред руху приводу.
std::optional<std::size_t> Dispatcher::allocate() noexcept {
    for (std::size_t n = 0; n < RingSize; ++n) {
        const std::size_t i = (head_ + n) % RingSize;
        if (ring_[i].pending()) continue;

        head_ = (i + 1) % RingSize;
        ring_[i] = Record{};
        return i;
    }
    return std::nullopt;
}

bool Dispatcher::queue_push(std::size_t slot) noexcept {
    if (queue_count_ >= QueueSize) return false;
    queue_[(queue_head_ + queue_count_) % QueueSize] = slot;
    ++queue_count_;
    return true;
}

std::optional<std::size_t> Dispatcher::queue_pop() noexcept {
    if (queue_count_ == 0) return std::nullopt;
    const std::size_t slot = queue_[queue_head_];
    queue_head_ = (queue_head_ + 1) % QueueSize;
    --queue_count_;
    return slot;
}

// Чи є далі в черзі свіжіша команда того самого призначення. Виконувати
// застарілу абсолютну команду — марний знос механіки: залп після сну інакше
// проганяє заслінку туди-сюди.
bool Dispatcher::superseded_later(const Record& record) const noexcept {
    if (record.type != Type::SetRelay && record.type != Type::GotoPos) return false;

    for (std::size_t n = 0; n < queue_count_; ++n) {
        const Record& other = ring_[queue_[(queue_head_ + n) % QueueSize]];
        if (other.state != State::Accepted || other.type != record.type) continue;
        if (record.type == Type::SetRelay) {
            if (other.payload_len < 1 || record.payload_len < 1) continue;
            if (other.payload[0] != record.payload[0]) continue;   // інший канал реле
        }
        return true;
    }
    return false;
}

std::expected<void, Error> Dispatcher::on_frame(std::span<const std::byte> bytes) {
    const auto parsed = parse_command(bytes);
    if (!parsed) {
        // Квитанції немає навмисно: у битому кадрі й токен битий, відповідати
        // нема кому й нема на що. Сервер розбереться повтором.
        ++stats_.dropped;
        std::cout << std::format("  --> [кадр {} B] відкинуто на вході: {}\n",
                                 bytes.size(), name(parsed.error()));
        return std::unexpected(parsed.error());
    }
    const Command& cmd = *parsed;

    std::cout << std::format("  --> {:<11} token=0x{:08X} seq={} ttl={} мс\n",
                             name(cmd.type), static_cast<std::uint32_t>(cmd.token & 0xFFFFFFFFu),
                             cmd.seq, cmd.ttl.count());

    // 1. Дедуплікація — ПЕРШОЮ, до перевірки лічильника. Легітимний повтор несе
    //    той самий seq, і перевірка порядку відкинула б його мовчки, залишивши
    //    сервер без квитанції назавжди.
    if (Record* dup = find(cmd.token); dup != nullptr) {
        ++stats_.duplicates;
        if (dup->pending()) {
            std::cout << "      [дедуп] токен уже в роботі — залізо не чіпаємо\n";
            emit(1, *dup);
        } else {
            std::cout << "      [дедуп] токен уже відпрацьовано — віддаємо збережений результат\n";
            emit(2, *dup);
        }
        return {};
    }

    // 2. Монотонний лічильник повідомлень: старий кадр із ефіру не пройде.
    if (cmd.seq <= last_seq_) {
        ++stats_.replays;
        std::cout << std::format("      [повтор] seq={} не більший за вже прийнятий {} — кадр знищено\n",
                                 cmd.seq, last_seq_);
        return std::unexpected(Error::Replay);
    }

    const Millis now = clock_.now();

    const auto slot = allocate();
    if (!slot) {
        std::cout << "      [кільце] вільних слотів немає — усі зайняті незавершеними командами\n";
        Record temporary;
        temporary.token  = cmd.token;
        temporary.type   = cmd.type;
        temporary.state  = State::Failed;
        temporary.result = Error::NoSlot;
        emit(2, temporary);
        return std::unexpected(Error::NoSlot);
    }

    Record& record = ring_[*slot];
    record.token       = cmd.token;
    record.type        = cmd.type;
    record.payload     = cmd.payload;
    record.payload_len = cmd.payload_len;
    record.received    = now;
    record.deadline    = now + cmd.ttl;
    last_seq_          = cmd.seq;

    // 3. Вхідний фільтр строку придатності. Шлюз віднімає час, проведений у
    //    своїй черзі, тож нульовий залишок означає прострочену команду.
    if (cmd.ttl == Millis{0}) {
        ++stats_.expired;
        std::cout << "      [ttl] залишок нульовий — команда протухла ще в мережі\n";
        record.state  = State::Expired;
        record.result = Error::Expired;
        emit(2, record);
        return std::unexpected(Error::Expired);
    }

    // 4. Фаза 1: пакет цілий, токен зафіксовано, команда прийнята до виконання.
    //    Сервер зупиняє таймер повторів.
    record.state = State::Accepted;
    emit(1, record);

    if (!queue_push(*slot)) {
        std::cout << "      [черга] переповнена — команду виконати нікуди\n";
        record.state  = State::Failed;
        record.result = Error::QueueFull;
        emit(2, record);
        return std::unexpected(Error::QueueFull);
    }

    return {};
}

void Dispatcher::finish(Record& record, State state, Error result, std::int32_t detail) {
    transaction_.reset();   // RAII: запис у FRAM закривається тут
    record.state  = state;
    record.result = result;
    record.detail = detail;
    emit(2, record);
    active_.reset();
}

void Dispatcher::tick() {
    const Millis now = clock_.now();

    // А. Команда в роботі: опитуємо привід і стежимо за строком виконання.
    if (active_) {
        Record& record = ring_[*active_];
        const auto outcome = actuator_.poll();

        if (!outcome) {
            // Передстартовий фільтр не рятує від затягнутого руху: перевіряємо
            // дедлайн і посеред виконання, знімаючи струм із драйвера.
            if (now >= record.deadline) {
                actuator_.abort();
                ++stats_.expired;
                std::cout << "      [ttl] строк вичерпано під час руху — операцію скасовано\n";
                finish(record, State::Expired, Error::Expired, actuator_.position());
            }
            return;   // привід зайнятий — черга чекає
        }

        if (outcome->error != Error::Ok) {
            std::cout << std::format("      [виконання] зрив: {}\n", name(outcome->error));
            finish(record, State::Failed, outcome->error, outcome->detail);
        } else {
            ++stats_.executed;
            finish(record, State::Succeeded, Error::Ok, outcome->detail);
        }
    }

    // Б. Привід вільний: дістаємо наступну команду з черги.
    while (!active_) {
        const auto slot = queue_pop();
        if (!slot) break;

        Record& record = ring_[*slot];
        if (record.state != State::Accepted) continue;   // слот уже закритий іншою гілкою

        // Передстартовий фільтр: остання перевірка перед подачею напруги.
        if (now >= record.deadline) {
            ++stats_.expired;
            std::cout << std::format("      [ttl] {} token=0x{:08X} простояв у черзі довше за строк"
                                     " — не пускаємо в залізо\n",
                                     name(record.type),
                                     static_cast<std::uint32_t>(record.token & 0xFFFFFFFFu));
            record.state  = State::Expired;
            record.result = Error::Expired;
            emit(2, record);
            continue;
        }

        if (superseded_later(record)) {
            ++stats_.superseded;
            std::cout << std::format("      [залп] {} token=0x{:08X} витіснено свіжішою командою"
                                     " того ж призначення\n",
                                     name(record.type),
                                     static_cast<std::uint32_t>(record.token & 0xFFFFFFFFu));
            record.state  = State::Expired;
            record.result = Error::Superseded;
            emit(2, record);
            continue;
        }

        // Слід у незалежній пам'яті ДО подачі струму: якщо живлення зникне
        // посеред руху, після перезапуску буде видно незавершений токен.
        transaction_.emplace(journal_, record.token, record.type);

        const auto started = actuator_.start(record.type, record.data());
        if (!started) {
            std::cout << std::format("      [виконання] залізо відмовило на старті: {}\n",
                                     name(started.error()));
            transaction_.reset();              // струм так і не пішов — запис у FRAM зайвий
            record.state  = State::Failed;
            record.result = started.error();
            emit(2, record);
            continue;
        }

        record.state = State::Executing;
        active_ = *slot;

        // Миттєві дії (реле) завершуються в тому ж такті — забираємо результат
        // одразу, щоб не тримати сервер в очікуванні зайвий цикл.
        if (const auto outcome = actuator_.poll(); outcome) {
            if (outcome->error != Error::Ok) {
                std::cout << std::format("      [виконання] зрив: {}\n", name(outcome->error));
                finish(record, State::Failed, outcome->error, outcome->detail);
            } else {
                ++stats_.executed;
                finish(record, State::Succeeded, Error::Ok, outcome->detail);
            }
        }
    }
}

void Dispatcher::simulate_power_loss() {
    if (transaction_) transaction_->release();   // запис у FRAM лишається відкритим
    transaction_.reset();

    ring_.fill(Record{});
    head_ = 0;
    queue_.fill(0);
    queue_head_ = 0;
    queue_count_ = 0;
    last_seq_ = 0;
    active_.reset();
}

void Dispatcher::recover_after_reset() {
    const auto entry = journal_.open_entry();
    if (!entry) return;

    std::cout << std::format("      [старт] у FRAM відкрита транзакція {} token=0x{:08X}"
                             " — рух обірвано живленням\n",
                             name(entry->type),
                             static_cast<std::uint32_t>(entry->token & 0xFFFFFFFFu));

    // Механізм у невизначеному стані: спершу зводимо його в безпечну точку.
    actuator_.home();
    journal_.clear();

    // Реєструємо токен як провалений. Без цього повтор із сервера виглядав би
    // новою командою — і насос налив би дозу вдруге.
    if (const auto slot = allocate(); slot) {
        Record& record = ring_[*slot];
        record.token    = entry->token;
        record.type     = entry->type;
        record.state    = State::Failed;
        record.result   = Error::PowerReset;
        record.received = clock_.now();
        record.deadline = clock_.now();
        emit(2, record);
    }
}

void Dispatcher::print_stats() const {
    std::cout << "\n--- підсумок диспетчера ---\n";
    std::cout << std::format("  виконано:          {}\n", stats_.executed);
    std::cout << std::format("  дублікатів:        {}\n", stats_.duplicates);
    std::cout << std::format("  протухло за TTL:   {}\n", stats_.expired);
    std::cout << std::format("  витіснено залпом:  {}\n", stats_.superseded);
    std::cout << std::format("  повторів з ефіру:  {}\n", stats_.replays);
    std::cout << std::format("  битих кадрів:      {}\n", stats_.dropped);
    std::cout << std::format("  пам'ять кільця:    {} байт ({} слотів)\n",
                             RingSize * sizeof(Record), RingSize);
}

}  // namespace cmdctl
