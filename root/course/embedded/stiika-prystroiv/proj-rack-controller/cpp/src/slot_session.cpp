#include "slot_session.hpp"

#include <format>
#include <thread>

#include <fcntl.h>
#include <sys/file.h>

namespace {

constexpr std::string_view kLockDir = "/tmp/dut-locks";

} // namespace

SlotSession::SlotSession(int slotId, UniqueFd lock, int mirrorFd)
    : slotId_{slotId},
      lock_{std::move(lock)},
      console_{slotId, mirrorFd},
      lines_{slotId},
      programmer_{slotId}
{
}

SlotSession SlotSession::acquire(int slotId, std::chrono::milliseconds wait, int mirrorFd)
{
    std::error_code ec;
    std::filesystem::create_directories(kLockDir, ec); // уже є — не помилка
    if (ec) {
        throw std::runtime_error{std::format("не створюється {}: {}", kLockDir, ec.message())};
    }

    const auto path = std::format("{}/slot_{:02d}.lock", kLockDir, slotId);
    UniqueFd lock{::open(path.c_str(), O_CREAT | O_RDWR | O_CLOEXEC, 0666)};
    if (!lock) {
        throwErrno(std::format("не відкривається {}", path));
    }

    const auto deadline = std::chrono::steady_clock::now() + wait;
    while (::flock(lock.get(), LOCK_EX | LOCK_NB) != 0) {
        if (errno != EWOULDBLOCK) {
            throwErrno(std::format("flock({})", path));
        }
        if (gStopRequested || std::chrono::steady_clock::now() >= deadline) {
            throw SlotBusy{std::format("слот {:02d} тримає інший прогін", slotId)};
        }
        std::this_thread::sleep_for(std::chrono::milliseconds{100});
    }

    // Слід для людини, яка прийде дивитися, хто ж тримає слот. Право володіння
    // дає flock, а не вміст файлу, тож помилку запису тут просто ігноруємо.
    if (::ftruncate(lock.get(), 0) == 0) {
        const auto note = std::format("pid={}\n", ::getpid());
        [[maybe_unused]] const auto written = ::write(lock.get(), note.data(), note.size());
    }

    // Ядро зніме flock навіть після SIGKILL, тому слот не зависає «зайнятим».
    return SlotSession{slotId, std::move(lock), mirrorFd};
}

void SlotSession::powerCycle(std::chrono::milliseconds offFor)
{
    lines_.vcc(false);
    std::this_thread::sleep_for(offFor);

    // Поки плата знеструмлена, у черзі могло осісти сміття з перехідних рівнів
    // на лінії RX. Чистимо саме тут — за мить до появи справжніх байтів.
    console_.flushInput();

    lines_.vcc(true);
    // Ніякої паузи «щоб плата встигла»: читання починається негайно, інакше ми
    // знову втрачаємо перші рядки завантажувача.
}

void SlotSession::boot(std::string_view banner, std::chrono::milliseconds timeout)
{
    powerCycle(kPowerOff);
    console_.expect(banner, timeout);
}

void SlotSession::flash(const std::filesystem::path& image)
{
    // Прошиваємо зі свіжого старту: плата, що зависла в перериванні або тримає
    // шину SWD, часто не дає налагоджувачу під'єднатися.
    powerCycle(kPowerOff);
    std::this_thread::sleep_for(kPowerSettle);
    programmer_.program(image);
}

void SlotSession::unbrick()
{
    // 1. Зняти живлення: BOOT0 читається лише при старті.
    lines_.vcc(false);
    std::this_thread::sleep_for(kPowerOff);

    {
        // BOOT0 має впасти навіть якщо стирання кине виняток — інакше слот
        // назавжди лишиться в завантажувачі, і наступний прогін не зрозуміє,
        // чому плата мовчить. У C це доводиться пам'ятати в кожній гілці.
        struct Boot0Guard {
            RackLines& lines;
            ~Boot0Guard()
            {
                try {
                    lines.boot0(false);
                } catch (...) {
                }
            }
        };

        // 2. Підняти BOOT0.
        lines_.boot0(true);
        Boot0Guard guard{lines_};

        // 3. Подати живлення — стартує фабричний завантажувач із ROM, а не збійний
        // код користувача, тож ані петля сторожового таймера, ані переконфігурований
        // SWD більше не заважають.
        console_.flushInput();
        lines_.vcc(true);
        std::this_thread::sleep_for(kPowerSettle + kBootRom);

        // 4. Стерти пошкоджену прошивку (за потреби — разом зі зняттям RDP).
        programmer_.massErase();
    }

    // 5. Холодний рестарт: після mass_erase і зняття захисту потрібен саме POR.
    powerCycle(kPowerOff);
}
