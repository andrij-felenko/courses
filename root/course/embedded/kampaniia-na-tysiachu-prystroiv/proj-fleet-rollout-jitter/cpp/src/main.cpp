// Прогін кампанії на одному вузлі парку — від номера когорти до підтвердження
// або відкату. Симульовані тут лише зовнішні речі: годинник, радіоканал і сам
// CDN; уся логіка вузла — та сама, що поїде на кристал.
//
//   ./ota_node          — вузол проходить випробування і підтверджує образ
//   ./ota_node crash    — новий образ падає на кожному старті; видно, як
//                         лічильник у незалежній пам'яті доводить до відкату
#include "cohort.hpp"
#include "rollout.hpp"
#include "storage.hpp"
#include "supervisor.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <optional>
#include <print>
#include <span>
#include <string_view>
#include <vector>

namespace {

using namespace std::chrono_literals;
using fleet::Bank;
using fleet::Millis;

constexpr std::uint32_t kImageLen = 96 * 1024;
constexpr std::uint32_t kBlockLen = 2048;
constexpr std::size_t   kFleetSize = 1000;
constexpr std::uint8_t  kStagePercent = 25;
constexpr auto kJitterWindow = std::chrono::duration_cast<Millis>(15min);
constexpr auto kTrialWindow = 1800s;
constexpr auto kTick = 60s;

// Маніфест кампанії, який вузол забрав із сервера. Сіль публікується разом із
// кампанією: інша кампанія — інша сіль — інше розбиття парку.
struct Manifest {
    std::uint32_t campaign_id;
    std::string_view salt;
    std::uint8_t stage_percent;
    std::uint32_t image_len;
    std::uint32_t image_crc;
};

// Годинник симуляції: кампанія розтягнута на години, і чекати їх немає сенсу.
Millis g_now{0};
void sleep_for(Millis d) { g_now += d; }

std::vector<std::byte> make_image(std::uint32_t version)
{
    // Замість справжнього образу — детермінований візерунок: важливо лише те,
    // що дві версії різні, а CRC відтворюваний.
    std::vector<std::byte> image(kImageLen);
    std::uint32_t x = 0x1234567u ^ version;
    for (std::byte& b : image) {
        x = x * 1664525u + 1013904223u;
        b = static_cast<std::byte>(x >> 24);
    }
    return image;
}

// Радіоканал у полі: приблизно кожна четверта сесія обривається.
class Cdn {
public:
    explicit Cdn(std::vector<std::byte> image) : image_(std::move(image)) {}

    [[nodiscard]] std::optional<std::span<const std::byte>>
    read(std::uint32_t offset, std::uint32_t len, fleet::Rng& rng) const
    {
        if (rng.below(100) < 25) {
            return std::nullopt;
        }
        return std::span{image_}.subspan(offset, len);
    }

    [[nodiscard]] std::span<const std::byte> whole() const { return image_; }

private:
    std::vector<std::byte> image_;
};

bool provision_factory_image(fleet::StateStore& store)
{
    fleet::RolloutState st = store.load();
    if (st.length_of(Bank::A) != 0) {
        return true;   // вузол уже прошитий на конвеєрі
    }

    const auto factory = make_image(1);
    fleet::BankWriter writer{Bank::A};
    if (const auto r = writer.erase().and_then([&] { return writer.write(0, factory); }); !r) {
        std::println("[вузол] заводський образ не записався: {}", fleet::describe(r.error()));
        return false;
    }

    st.active = Bank::A;
    st.trial_pending = false;
    st.boot_failures = 0;
    st.length_of(Bank::A) = kImageLen;
    st.crc_of(Bank::A) = fleet::bank_crc(Bank::A, kImageLen);
    return store.save(st).has_value();
}

// Перед кампанією розподіл перевіряють на всій множині серійних номерів парку.
void survey_fleet(const Manifest& manifest, const fleet::DeviceId& own_id)
{
    std::vector<fleet::DeviceId> parc(kFleetSize, own_id);
    for (std::size_t i = 0; i < kFleetSize; ++i) {
        parc[i][12] = static_cast<std::byte>(i);
        parc[i][13] = static_cast<std::byte>(i >> 8);
        parc[i][14] = static_cast<std::byte>(i >> 16);
        parc[i][15] = static_cast<std::byte>(i >> 24);
    }

    for (const auto [kind, label] : {std::pair{fleet::HashKind::Sha256, "SHA-256"},
                                     std::pair{fleet::HashKind::Fnv1a, "FNV-1a "}}) {
        const fleet::CohortAssigner assigner{manifest.salt, kind};
        const auto d = assigner.survey(parc);
        std::println("[парк] {}: хі-квадрат {:.1f}, кошики {}..{} -> {}",
                     label, d.chi_square, d.min, d.max,
                     d.acceptable() ? "рівномірно" : "НЕРІВНОМІРНО");
    }
}

bool download_image(const Manifest& manifest, const Cdn& cdn, fleet::Rng& rng, Bank target)
{
    fleet::BankWriter writer{target};
    if (const auto r = writer.erase(); !r) {
        std::println("[ota] банк не стерся: {}", fleet::describe(r.error()));
        return false;
    }

    fleet::DecorrelatedBackoff backoff{2s, 5min};
    unsigned retries = 0;

    for (std::uint32_t off = 0; off < manifest.image_len; off += kBlockLen) {
        const std::uint32_t len = std::min(kBlockLen, manifest.image_len - off);

        std::optional<std::span<const std::byte>> block;
        while (!(block = cdn.read(off, len, rng))) {
            const Millis wait = backoff.next(rng);
            if (++retries > 200) {
                std::println("[ota] канал не тримає сесію, кампанію відкладено");
                return false;
            }
            sleep_for(wait);
        }
        backoff.reset();

        if (const auto r = writer.write(off, *block); !r) {
            std::println("[ota] помилка запису на зсуві {}: {}", off, fleet::describe(r.error()));
            return false;
        }
    }

    std::println("[ota] образ завантажено, повторів через обриви: {}", retries);

    if (fleet::bank_crc(target, manifest.image_len) != manifest.image_crc) {
        std::println("[ota] CRC не збігся з маніфестом — банк не активуємо");
        return false;
    }
    return true;
}

// Застосунок, який стартував із вибраного банку. Хибне значення означає
// перезавантаження без підтвердження.
bool app_run(fleet::StateStore& store, const fleet::BootSelector::Decision& d, bool inject_crash)
{
    fleet::TrialSupervisor trial{store, kTrialWindow};
    if (!trial.on_trial()) {
        std::println("[app] звичайний старт із банку {}", fleet::name(d.bank));
        return true;
    }

    std::println("[app] випробувальний термін, банк {}, аварійних стартів {}",
                 fleet::name(d.bank), d.failures);

    for (;;) {
        if (inject_crash && trial.elapsed() >= 120s) {
            // Паніка ядра: підтвердження не сталося, стан у незалежній пам'яті
            // лишився як був.
            std::println("[app] паніка на {} — перезавантаження", trial.elapsed());
            return false;
        }

        // Самодіагностика: шини сенсорів, живлення, цілісність конфігурації.
        // Обмін із бекендом іде довше — він вимагає TLS і живого каналу.
        fleet::TrialSupervisor::Health health{
            .self_test = trial.elapsed() >= 180s ? std::optional{true} : std::nullopt,
            .backend   = trial.elapsed() >= 300s ? std::optional{true} : std::nullopt};

        const auto outcome = trial.tick(kTick, health);
        sleep_for(std::chrono::duration_cast<Millis>(kTick));

        if (!outcome) {
            std::println("[app] стан не записався: {}", fleet::describe(outcome.error()));
            return false;
        }
        if (*outcome == fleet::TrialSupervisor::Outcome::Committed) {
            std::println("[app] образ підтверджено на {}", trial.elapsed());
            return true;
        }
        if (*outcome == fleet::TrialSupervisor::Outcome::RolledBack) {
            std::println("[app] відкат на попередній банк — перезавантаження");
            return false;
        }
    }
}

} // namespace

int main(int argc, char** argv)
{
    const bool inject_crash = (argc > 1 && std::string_view{argv[1]} == "crash");

    const fleet::DeviceId id = fleet::chip_id();
    const Cdn cdn{make_image(2)};

    const Manifest manifest{
        .campaign_id = 0x2026'0829u,
        .salt = "rollout-2026-08-r3",
        .stage_percent = kStagePercent,
        .image_len = kImageLen,
        // На сервері цю суму рахують один раз і підписують разом із маніфестом.
        .image_crc = fleet::crc32(cdn.whole())};

    fleet::StateStore store;
    if (!provision_factory_image(store)) {
        return 1;
    }

    survey_fleet(manifest, id);

    const fleet::CohortAssigner assigner{manifest.salt};
    std::println("[вузол] когорта {}, поточна фаза {}%", assigner.bucket(id), manifest.stage_percent);

    if (!assigner.eligible(id, manifest.stage_percent)) {
        std::println("[вузол] фаза цього вузла ще не настала — чекаємо");
        return 0;
    }

    fleet::Rng rng{id};
    const Millis delay = fleet::initial_jitter(rng, kJitterWindow);
    std::println("[вузол] початковий джитер {} у вікні {}", delay, kJitterWindow);
    sleep_for(delay);

    const Bank target = fleet::other(store.load().active);
    if (!download_image(manifest, cdn, rng, target)) {
        return 1;
    }
    if (const auto armed = fleet::TrialSupervisor::arm(store, target, manifest.campaign_id,
                                                       manifest.image_len, manifest.image_crc);
        !armed) {
        std::println("[ota] покажчик завантаження не переставлено: {}",
                     fleet::describe(armed.error()));
        return 1;
    }
    std::println("[ota] банк {} озброєно, перезавантаження", fleet::name(target));

    // Цикли скидання. На кристалі кожен виток це справжній reset.
    fleet::BootSelector selector{store};
    for (unsigned cycle = 1; cycle <= 8; ++cycle) {
        std::println("\n--- скидання #{} ---", cycle);

        const auto decision = selector.select();
        if (decision.verdict == fleet::BootSelector::Verdict::NoImage) {
            std::println("[boot] цілого образу немає — лишаємось у завантажувачі");
            return 2;
        }
        if (decision.verdict == fleet::BootSelector::Verdict::RolledBack) {
            std::println("[boot] лічильник збоїв вичерпано, повернулись на банк {}",
                         fleet::name(decision.bank));
        }
        fleet::BootSelector::jump(decision.entry);

        if (app_run(store, decision, inject_crash && decision.bank == Bank::B)) {
            const fleet::RolloutState st = store.load();
            std::println("\n[підсумок] банк {}, випробування {}, аварійних стартів {}",
                         fleet::name(st.active),
                         st.trial_pending ? "триває" : "завершено",
                         st.boot_failures);
            return 0;
        }
    }

    std::println("[вузол] вичерпано ліміт скидань симуляції");
    return 3;
}
