#include "at/engine.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <utility>

namespace at {
namespace {

/* Тимчасова помилка означає «спробуй ще», остаточна — «не буде». Голе ERROR
   завжди остаточне: повторювати синтаксично неправильну команду безглуздо. */
[[nodiscard]] bool error_is_temporary(std::string_view line) noexcept
{
    static constexpr std::array<int, 3> kTemporaryCodes{
        3,    // operation not allowed — стек мережі ще піднімається
        14,   // SIM busy — картка зайнята внутрішньою операцією
        100,  // unknown — модуль ще не готовий відповісти по суті
    };

    const auto marker = line.find("ERROR:");
    if (marker == std::string_view::npos) {
        return false;
    }

    std::string_view tail = line.substr(marker + std::string_view{"ERROR:"}.size());
    while (!tail.empty() && tail.front() == ' ') {
        tail.remove_prefix(1);
    }

    int code = 0;
    const auto [ptr, ec] = std::from_chars(tail.data(), tail.data() + tail.size(), code);
    if (ec != std::errc{}) {
        return false;   // текстовий опис замість коду (+CME ERROR: SIM busy)
    }
    return std::ranges::find(kTemporaryCodes, code) != kTemporaryCodes.end();
}

[[nodiscard]] std::span<const std::byte> as_wire(std::string_view text) noexcept
{
    return std::as_bytes(std::span{text.data(), text.size()});
}

}  // namespace

std::string_view Engine::to_string(State state) noexcept
{
    switch (state) {
        case State::Idle:              return "IDLE";
        case State::Send:              return "SEND";
        case State::WaitPrompt:        return "WAIT_PROMPT";
        case State::WaitResponse:      return "WAIT_RESPONSE";
        case State::RetryDelay:        return "RETRY_DELAY";
        case State::TimeoutEscalation: return "TIMEOUT_ESCALATION";
    }
    return "?";
}

Engine::Engine(Hooks hooks) noexcept : hooks_{std::move(hooks)} {}

bool Engine::register_urc(std::string_view prefix, UrcHandler handler) noexcept
{
    return urc_.add(prefix, std::move(handler));
}

bool Engine::send(Command command) noexcept
{
    if (command.text.empty() || command.text.truncated() || command.expect.truncated()) {
        return false;
    }
    /* Запрошення без даних — помилка виклику: рушій дочекався б '>' і завис. */
    if (command.wait_prompt && command.payload.empty()) {
        return false;
    }
    command.attempt = 0;
    return queue_.push(std::move(command));
}

bool Engine::retries_left() const noexcept
{
    return active_.has_value() && active_->attempt < active_->retries;
}

bool Engine::expired(Millis now, Millis limit) const noexcept
{
    // Беззнакове віднімання обгортається саме там, де переповнюється SysTick.
    return (now - timer_start_) >= limit;
}

void Engine::finish(const Result& result) noexcept
{
    Command done = std::move(*active_);
    active_.reset();
    state_ = State::Idle;

    if (result.has_value()) {
        consecutive_timeouts_ = 0;
        /* Луна вимикається лише за підтвердженим ATE0: доти парсер
           зобов'язаний відкидати рядки, рівні надісланій команді. */
        if (done.text == "ATE0") {
            echo_active_ = false;
        }
    }

    if (done.done) {
        // Колбек має право одразу покласти нову команду: рушій уже в Idle,
        // а активної команди більше немає — крутити нічого.
        done.done(result);
    }
}

void Engine::schedule_retry(Millis now) noexcept
{
    ++active_->attempt;
    ++stats_.retries;
    /* Тіло попередньої спроби більше не наше. Не скинути його — означає
       віддати в колбек повтору рядок, якого модуль на цю спробу не присилав:
       "+CSQ: 24,99" з невдалої спроби виглядав би як свіжий рівень сигналу. */
    response_.clear();
    timer_start_ = now;
    state_ = State::RetryDelay;
}

void Engine::abort_queue() noexcept
{
    /* Скільки саме скасовувати — вирішуємо ДО першого колбека. Обробник
       Aborted має повне право поставити свою команду наново, і звичайний
       «викачуй, поки черга не порожня» ковтав би її знову й знову. */
    std::size_t victims = queue_.size();

    while (victims-- > 0) {
        auto victim = queue_.pop();
        if (!victim) {
            break;
        }
        if (victim->done) {
            victim->done(Result{std::unexpected{Failure{Status::Aborted, {}}}});
        }
    }
}

void Engine::escalate(std::uint16_t head) noexcept
{
    /* У буфері лишився хвіст напівприйнятої відповіді. Не викинути його —
       означає зсунути розбір наступної команди на одну відповідь уперед. */
    ring_.flush(head);

    ++stats_.timeouts;
    ++consecutive_timeouts_;

    const bool stuck = (consecutive_timeouts_ >= config::kTimeoutEscalationLimit);

    if (stuck) {
        /* Модуль вважається завислим. Тримати чергу немає сенсу: кожен, хто
           чекає, дістає Aborted — інакше прикладний код лишиться з «висячою»
           операцією назавжди.

           Чергу згортаємо ДО колбека таймауту, а не після. Порядок тут не
           косметичний: колбек майже завжди ставить у чергу відновлювальну
           команду, і скасування, виконане після нього, викинуло б саме її —
           тобто вбило б ту єдину спробу, заради якої аварію й обробляють. */
        abort_queue();
        consecutive_timeouts_ = 0;
        echo_active_ = true;   // після PWRKEY модуль знову в ATE1
        ++stats_.recoveries;
    }

    finish(Result{std::unexpected{Failure{Status::Timeout, {}}}});   // переводить у Idle

    /* Смикати живлення — теж після колбека: гачок має право покласти власну
       стартову послідовність, і вона мусить лягти на вже порожню чергу. */
    if (stuck && hooks_.on_module_stuck) {
        hooks_.on_module_stuck();
    }
}

void Engine::on_line(std::string_view line, Millis now) noexcept
{
    const bool waiting = (state_ == State::WaitResponse || state_ == State::WaitPrompt);
    if (!waiting || !active_.has_value()) {
        /* Рядок поза контекстом: спізніла відповідь на команду, яку ми вже
           закрили за таймаутом. Тихо викидаємо. */
        ++stats_.orphan_lines;
        return;
    }

    if (echo_active_ && active_->text == line) {
        ++stats_.echo_dropped;
        return;
    }

    /* Помилка розглядається першою й однаково в обох станах очікування.
       На AT+QISEND у закритий сокет модуль відповідає простим "ERROR" і
       запрошення не надсилає ВЗАГАЛІ — рушій, який у стані WaitPrompt
       дивиться самі лише сирі байти, простояв би тут увесь таймаут. */
    if (line == "ERROR" || line.starts_with("+CME ERROR:") || line.starts_with("+CMS ERROR:")) {
        if (error_is_temporary(line) && retries_left()) {
            schedule_retry(now);
        } else {
            finish(Result{std::unexpected{Failure{Status::Error, line}}});
        }
        return;
    }

    if (state_ == State::WaitPrompt) {
        /* Усе інше до запрошення — шум: тіла відповіді тут не буває, а
           фінальне "OK" приходить уже після відправлених сирих байтів. */
        return;
    }

    if (line == "OK" || line == "SEND OK") {
        finish(Result{response_.view()});
        return;
    }

    /* Не фінальний маркер — тіло відповіді. Коли префікс заявлено, беремо
       лише його; коли ні — тримаємо останній змістовний рядок. */
    if (!active_->expect.empty() && !line.starts_with(active_->expect.view())) {
        return;
    }
    response_ = StaticString<config::kMaxLine>{line};
}

void Engine::pump_rx(std::uint16_t head, Millis now) noexcept
{
    for (;;) {
        const auto line = reader_.next(head);

        if (!line) {
            if (line.error() == LineReader::Event::NoData) {
                break;
            }
            if (line.error() == LineReader::Event::Overflow) {
                ++stats_.overflows;
            }
            continue;   // Blank або Overflow — читаємо далі
        }

        ++stats_.lines_in;

        /* URC має пріоритет над контекстом команди: розрив сокета може прийти
           рівно між рядками очікуваної відповіді. */
        if (urc_.dispatch(*line)) {
            ++stats_.urc_lines;
            continue;
        }

        on_line(*line, now);
    }

    /* Запрошення '>' не завершується переводом рядка, тож лінійний читач його
       не побачить ніколи — сирі байти добираємо окремо, і саме ПІСЛЯ рядків.
       Порядок тут робить дві речі. По-перше, перед запрошенням у дроті стоять
       "\r\n" і луна команди — вони мусять поїхати як рядки. По-друге, шукати
       '>' наосліп по всьому буферу небезпечно: символ трапляється всередині
       URC, і сліпий пошук з'їв би повідомлення разом із ним. Після вичитки
       рядків лишається тільки незавершений хвіст — там запрошення й живе. */
    if (state_ == State::WaitPrompt) {
        if (ring_.take_upto(head, static_cast<std::uint8_t>(config::kPromptChar))) {
            hooks_.uart_tx(active_->payload);
            timer_start_ = now;
            state_ = State::WaitResponse;
        }
    }
}

void Engine::run_fsm(std::uint16_t head, Millis now) noexcept
{
    switch (state_) {
        case State::Idle:
            if (auto next = queue_.pop()) {
                active_ = std::move(next);
                response_.clear();
                state_ = State::Send;
            }
            break;

        case State::Send: {
            static constexpr std::array<std::byte, 2> kCrLf{std::byte{'\r'}, std::byte{'\n'}};
            hooks_.uart_tx(as_wire(active_->text.view()));
            hooks_.uart_tx(kCrLf);
            timer_start_ = now;
            state_ = active_->wait_prompt ? State::WaitPrompt : State::WaitResponse;
            break;
        }

        case State::WaitPrompt:
        case State::WaitResponse:
            if (expired(now, active_->timeout)) {
                if (retries_left()) {
                    /* Хвіст відповіді, що не дійшла, для повтору вже сміття:
                       лишити його — значить прочитати шматок старої спроби
                       як початок нової. */
                    ring_.flush(head);
                    schedule_retry(now);
                } else {
                    state_ = State::TimeoutEscalation;
                }
            }
            break;

        case State::RetryDelay:
            if (expired(now, config::kRetryDelay)) {
                state_ = State::Send;
            }
            break;

        case State::TimeoutEscalation:
            escalate(head);
            break;
    }
}

void Engine::poll(std::uint16_t cndtr) noexcept
{
    const Millis now = hooks_.tick();
    const std::uint16_t head = RingBuffer::head_from_cndtr(cndtr);

    pump_rx(head, now);
    run_fsm(head, now);
}

}  // namespace at
