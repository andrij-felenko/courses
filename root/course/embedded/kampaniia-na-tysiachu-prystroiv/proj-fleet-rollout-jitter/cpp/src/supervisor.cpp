#include "supervisor.hpp"

#include <print>

namespace fleet {
namespace {

bool bank_intact(const RolloutState& st, Bank bank)
{
    const std::uint32_t len = st.length_of(bank);
    if (len == 0) {
        return false;   // банк порожній або ніколи не реєструвався
    }
    return bank_crc(bank, len) == st.crc_of(bank);
}

} // namespace

TrialSupervisor::TrialSupervisor(StateStore& store, Seconds window)
    : store_(store), state_(store.load()), window_(window)
{
}

std::expected<void, StorageError> TrialSupervisor::arm(StateStore& store, Bank target,
                                                       std::uint32_t campaign_id,
                                                       std::uint32_t image_len,
                                                       std::uint32_t image_crc)
{
    // Покажчик завантаження переставляємо ЛИШЕ після того, як образ у банку
    // зійшовся за контрольною сумою.
    if (bank_crc(target, image_len) != image_crc) {
        return std::unexpected(StorageError::CrcMismatch);
    }

    RolloutState st = store.load();
    st.active = target;
    st.trial_pending = true;
    st.boot_failures = 0;
    st.campaign_id = campaign_id;
    st.length_of(target) = image_len;
    st.crc_of(target) = image_crc;
    return store.save(st);
}

std::expected<TrialSupervisor::Outcome, StorageError>
TrialSupervisor::tick(Seconds dt, Health health)
{
    if (!state_.trial_pending) {
        return Outcome::Committed;   // цей старт не є випробуванням
    }

    // Явний дефект не чекає таймауту: сенсорна шина, яка не відповідає, за
    // півгодини сама не полагодиться.
    if (health.self_test == false || health.backend == false) {
        return rollback();
    }

    self_test_passed_ = self_test_passed_ || health.self_test.value_or(false);
    backend_confirmed_ = backend_confirmed_ || health.backend.value_or(false);

    // Обидві умови разом — і тільки разом. Підтвердження одразу після входу в
    // main() лишає в полі вузол, який падає на першому ж рукостисканні TLS.
    if (self_test_passed_ && backend_confirmed_) {
        return commit();
    }

    elapsed_ += dt;
    if (elapsed_ >= window_) {
        // Вузол не впав, але й не довів життєздатності.
        return rollback();
    }
    return Outcome::Running;
}

std::expected<TrialSupervisor::Outcome, StorageError> TrialSupervisor::commit()
{
    state_.trial_pending = false;
    state_.boot_failures = 0;
    return store_.save(state_).transform([] { return Outcome::Committed; });
}

std::expected<TrialSupervisor::Outcome, StorageError> TrialSupervisor::rollback()
{
    const Bank previous = other(state_.active);

    // Відкат має сенс лише тоді, коли старий образ на місці й цілий. Якщо ні —
    // лишаємо прапорець випробування: далі рішення за завантажувачем.
    if (!bank_intact(state_, previous)) {
        return Outcome::Running;
    }

    state_.active = previous;
    state_.trial_pending = false;
    state_.boot_failures = 0;
    return store_.save(state_).transform([] { return Outcome::RolledBack; });
}

BootSelector::Decision BootSelector::select()
{
    RolloutState st = store_.load();
    bool rolled_back = false;
    bool dirty = false;

    // Прапорець ще стоїть — попередній старт нового образу не дійшов до
    // підтвердження: паніка ядра, сторожовий таймер або зникнення живлення.
    // Лічильник живе в незалежній пам'яті, тому переживає все це.
    if (st.trial_pending) {
        if (st.boot_failures < 0xFF) {
            ++st.boot_failures;
        }
        dirty = true;

        if (st.boot_failures >= kMaxAllowedCrashes) {
            st.active = other(st.active);
            st.trial_pending = false;
            st.boot_failures = 0;
            rolled_back = true;
        }
    }

    // Цілісність вибраного банку перевіряємо завжди: образ міг постраждати від
    // обірваного запису або зношеного сектора.
    if (!bank_intact(st, st.active)) {
        if (bank_intact(st, other(st.active))) {
            st.active = other(st.active);
            st.trial_pending = false;
            st.boot_failures = 0;
            rolled_back = true;
            dirty = true;
        } else {
            if (dirty) {
                (void)store_.save(st);
            }
            return Decision{Verdict::NoImage, st.active, 0, st.boot_failures};
        }
    }

    if (dirty) {
        (void)store_.save(st);
    }

    return Decision{rolled_back ? Verdict::RolledBack : Verdict::Run,
                    st.active, bank_base(st.active), st.boot_failures};
}

#if defined(__arm__)

// Адреси регістрів ядра Cortex-M — з архітектурного довідника, без сторонніх
// заголовків: завантажувач збирається окремо й нічого зайвого не тягне.
namespace {
volatile std::uint32_t& scb_vtor()
{
    return *reinterpret_cast<volatile std::uint32_t*>(0xE000ED08u);
}
} // namespace

void BootSelector::jump(std::uint32_t entry)
{
    const auto* vectors = reinterpret_cast<const std::uint32_t*>(entry);
    const std::uint32_t stack_top = vectors[0];
    const std::uint32_t reset_handler = vectors[1];

    asm volatile("cpsid i" ::: "memory");   // переривання ще від старого образу
    scb_vtor() = entry;
    asm volatile("dsb; isb" ::: "memory");
    asm volatile("msr msp, %0" :: "r"(stack_top));
    asm volatile("bx %0" :: "r"(reset_handler));

    for (;;) { }
}

#else

void BootSelector::jump(std::uint32_t entry)
{
    // На хості стрибка немає: далі main просто викликає застосунок.
    std::println("[boot] VTOR = 0x{:08X}, передаємо керування", entry);
}

#endif

} // namespace fleet
