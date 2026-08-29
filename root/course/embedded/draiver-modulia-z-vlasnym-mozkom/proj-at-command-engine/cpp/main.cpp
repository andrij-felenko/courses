/* Демонстраційний прогін AT-рушія проти симулятора модуля.

   На залізі main виглядав би так само, тільки замість FakeModem стояли б
   HAL_UART_Transmit_DMA і HAL_GetTick, а Engine::poll викликався б із
   головного циклу або з нитки RTOS. */

#include <format>
#include <iostream>
#include <optional>
#include <span>
#include <string_view>

#include "at/engine.hpp"
#include "sim/fake_modem.hpp"

namespace {

void report(at::Millis now, std::string_view what, const at::Result& result)
{
    if (result) {
        std::cout << std::format("[{:4} мс] {:<26} → OK      {}\n",
                                 now.count(), what, *result);
    } else {
        std::cout << std::format("[{:4} мс] {:<26} → {:<7} {}\n",
                                 now.count(), what,
                                 at::to_string(result.error().status),
                                 result.error().detail);
    }
}

/* Сирі байти, які підуть у дріт після запрошення '>'. Статичні: пам'ять
   мусить жити до виклику колбека. */
constexpr std::string_view kHttpRequest{"GET / HTTP/1.0\r\n\r\n"};

[[nodiscard]] std::span<const std::byte> http_payload() noexcept
{
    return std::as_bytes(std::span{kHttpRequest.data(), kHttpRequest.size()});
}

}  // namespace

int main()
{
    at::Millis now{0};
    std::optional<sim::FakeModem> modem;   // потребує буфера рушія, тож пізніше

    at::Engine engine{at::Engine::Hooks{
        .uart_tx = [&modem, &now](std::span<const std::byte> data) { modem->on_tx(data, now); },
        .tick = [&now] { return now; },
        .on_module_stuck = [&now] {
            std::cout << std::format("[{:4} мс] ВІДНОВЛЕННЯ: модуль не відповідає — смикаємо PWRKEY\n",
                                     now.count());
        },
    }};

    // Симулятор пише в той самий масив, який на залізі був би ціллю DMA.
    modem.emplace(engine.rx_target());

    engine.register_urc("+QIURC: \"closed\"", [&engine, &now](std::string_view line) {
        std::cout << std::format("[{:4} мс] URC розрив сокета: {}\n", now.count(), line);

        /* Реентерабельність: команду ставимо в чергу прямо звідси. Це можна
           саме тому, що URC розбирається в контексті головного циклу, а черга
           захищена критичною секцією. */
        const bool queued = engine.send(at::Command{
            .text = "AT+QIOPEN=1,0,\"TCP\",\"example.net\",80,0,1",
            .timeout = at::Millis{500},
            .retries = 1,
            .done = [&now](const at::Result& r) { report(now, "AT+QIOPEN (з URC)", r); },
        });
        if (!queued) {
            std::cout << std::format("[{:4} мс] черга переповнена, перевідкриття відкладено\n",
                                     now.count());
        }
    });

    engine.register_urc("+QIOPEN:", [&now](std::string_view line) {
        std::cout << std::format("[{:4} мс] URC сокет піднято: {}\n", now.count(), line);
    });

    for (const std::string_view prefix : {"+QIURC:", "RING", "+CMTI:"}) {
        engine.register_urc(prefix, [&now](std::string_view line) {
            std::cout << std::format("[{:4} мс] URC: {}\n", now.count(), line);
        });
    }

    const auto submit = [&engine, &now](at::Command cmd, std::string_view label) {
        if (!engine.send(std::move(cmd))) {
            std::cout << std::format("[{:4} мс] черга не прийняла {}\n", now.count(), label);
        }
    };

    submit(at::Command{
               .text = "ATE0",
               .timeout = at::Millis{300},
               .retries = 2,
               .done = [&now](const at::Result& r) { report(now, "ATE0", r); },
           },
           "ATE0");

    submit(at::Command{
               .text = "AT+CFUN=1",
               .timeout = at::Millis{1000},
               .retries = 2,
               .done = [&now](const at::Result& r) { report(now, "AT+CFUN=1", r); },
           },
           "AT+CFUN=1");

    submit(at::Command{
               .text = "AT+CSQ",
               .expect = "+CSQ:",
               .timeout = at::Millis{500},
               .done = [&now](const at::Result& r) { report(now, "AT+CSQ", r); },
           },
           "AT+CSQ");

    // Команда з запрошенням: після '>' у дріт ідуть сирі байти.
    submit(at::Command{
               .text = "AT+QISEND=0,18",
               .payload = http_payload(),
               .timeout = at::Millis{1000},
               .wait_prompt = true,
               .done = [&now](const at::Result& r) { report(now, "AT+QISEND", r); },
           },
           "AT+QISEND");

    /* Та сама команда, але в закритий сокет: модуль відповість ERROR і
       запрошення не надішле ніколи. Рушій зобов'язаний закрити команду
       одразу, а не простояти цілу секунду в очікуванні '>'. */
    submit(at::Command{
               .text = "AT+QISEND=1,4",
               .payload = http_payload().first(4),
               .timeout = at::Millis{1000},
               .wait_prompt = true,
               .done = [&now](const at::Result& r) { report(now, "AT+QISEND (закритий)", r); },
           },
           "AT+QISEND (закритий)");

    /* Три команди, на які модуль мовчить: показують ескалацію таймауту й
       аварійне відновлення після третьої поспіль. */
    for (const std::string_view text : {"AT+QIDEACT=0", "AT+QIDEACT=1", "AT+QIDEACT=2"}) {
        submit(at::Command{
                   .text = text,
                   .timeout = at::Millis{250},
                   .done = [&now, text](const at::Result& r) { report(now, text, r); },
               },
               text);
    }

    bool late_probe_sent = false;

    for (now = at::Millis{0}; now < at::Millis{3000}; now += at::Millis{5}) {
        modem->tick(now);
        engine.poll(modem->cndtr());

        // Після аварійного відновлення рушій мусить працювати далі.
        if (!late_probe_sent && now >= at::Millis{2000}) {
            late_probe_sent = true;
            submit(at::Command{
                       .text = "AT+CSQ",
                       .expect = "+CSQ:",
                       .timeout = at::Millis{500},
                       .done = [&now](const at::Result& r) { report(now, "AT+CSQ (після відновлення)", r); },
                   },
                   "AT+CSQ (після відновлення)");
        }
    }

    const at::Engine::Stats& s = engine.stats();
    std::cout << std::format(
        "\nПідсумок: рядків {}, з них URC {}, луни відкинуто {},\n"
        "          сиріт {}, переповнень рядка {},\n"
        "          повторів {}, таймаутів {}, відновлень {}\n",
        s.lines_in, s.urc_lines, s.echo_dropped, s.orphan_lines, s.overflows,
        s.retries, s.timeouts, s.recoveries);

    return 0;
}
