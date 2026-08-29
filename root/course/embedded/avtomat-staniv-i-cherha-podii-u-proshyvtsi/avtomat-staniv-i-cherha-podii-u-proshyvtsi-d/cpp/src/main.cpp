#include <cstdint>
#include <variant>

#include "evse/cp_line.hpp"
#include "evse/event.hpp"

#include "system.hpp"

/*
 * Головний цикл усієї прошивки. Він не знає ні про зарядну станцію, ні про
 * лінію пілота: його робота — витягти подію, віддати її автомату й заснути,
 * коли віддавати нічого.
 */
int main()
{
    auto& board = app::board();

    app::Controller controller{board, app::g_timers};
    controller.start();

    evse::CpDebouncer cp;
    std::uint32_t     lastDropped = 0;

    for (;;) {
        while (const auto stamped = app::g_queue.pop()) {
            /* Повільні опитування живуть тут, у потоці головного циклу, а не
             * в обробнику таймера. */
            if (std::holds_alternative<evse::Tick10ms>(stamped->event)) {
                const bool pwmActive = board.pilotPeriod().count() != 0;
                const auto raw = evse::classify(board.pilotHigh(), board.pilotLow(),
                                                board.pilotPeriod(), pwmActive);
                if (const auto changed = cp.update(raw)) {
                    controller.dispatch(evse::CpChanged{*changed});
                }
            }

            /* Run-To-Completion: подія обробляється до кінця, і лише потім
             * береться наступна. Усередині dispatch() ніхто не чекає й не
             * спить, тому черга не встигає накопичитися. */
            controller.dispatch(stamped->event);
        }

        /*
         * Утрата події означає, що ми проґавили щось невідоме — можливо, саме
         * аварію. Єдина безпечна відповідь — знеструмити лінію.
         */
        if (const auto dropped = app::g_queue.dropped(); dropped != lastDropped) {
            lastDropped = dropped;
            controller.dispatch(evse::QueueOverflow{});
            continue;
        }

        /*
         * Перевірка порожньої черги й засинання мусять бути неподільні. Якби
         * переривання вклинилося між ними, воно поклало б подію в чергу вже
         * після перевірки — і ядро заснуло б до наступного, ні з чим не
         * пов'язаного переривання. WFI прокидається й із забороненими
         * перериваннями, тож заборона тут не заважає, а рятує.
         */
        {
            const app::Board::IrqLock guard;
            if (app::g_queue.empty()) {
                board.waitForInterrupt();
            }
        }
    }
}
