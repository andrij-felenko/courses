// main.cpp — стенд імітації сузір'я GPS L1 C/A: ефемериди → геометрія → I/Q
// для SDR і синхронне керування атенюатором.
#include <algorithm>
#include <csignal>
#include <cstdlib>
#include <expected>
#include <format>
#include <fstream>
#include <iostream>
#include <numbers>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include "attenuator.hpp"
#include "ephemeris.hpp"
#include "geometry.hpp"
#include "nav_frame.hpp"
#include "synthesizer.hpp"

namespace {

using namespace gnss;

constexpr double kPi              = std::numbers::pi;
constexpr double kSampleRateSps   = 2600000.0;
constexpr double kEpochSeconds    = 0.001;                 // один кодовий період
constexpr std::size_t kSamplesPerEpoch = 2600;
constexpr long   kGeometryEvery   = 100;                   // епох між перерахунком
constexpr long   kAttenuatorEvery = 200;
constexpr double kElevationMask   = 5.0 * kPi / 180.0;
constexpr double kDacScale        = 1500.0;

// Бюджет рівнів: що видає SDR і що має дійти до входу приймача.
constexpr double kSdrOutputDbm  = 0.0;
constexpr double kZenithRxDbm   = -128.5;
constexpr double kNominalRangeM = 20200000.0;

volatile std::sig_atomic_t g_stop = 0;
extern "C" void on_sigint(int) { g_stop = 1; }

struct Config {
    std::string rinex, port, out{"-"};
    double seconds{60.0};
    double lat_deg{50.45}, lon_deg{30.52}, alt_m{180.0};
    double speed_ms{0.0}, heading_deg{90.0};
    double mp_height{1.5}, mp_gamma{0.5}, humidity{0.6};
    double fixed_pad_db{70.0}, clock_drift_ppb{5.0};
    double leap_at{-1.0};
    bool   rollover{false};
};

void usage(std::string_view argv0)
{
    std::cerr << std::format(
        "використання: {} --rinex FILE --port DEV [опції]\n"
        "  --out FILE       куди писати I/Q (типово «-», тобто stdout)\n"
        "  --sec N          тривалість прогону, с\n"
        "  --lat/--lon/--alt координати старту (градуси, метри)\n"
        "  --speed/--course  швидкість, м/с, і курс, градуси\n"
        "  --mp-height H --mp-gamma G  висота антени й коефіцієнт відбиття\n"
        "  --fixed-pad DB   каскад фіксованих атенюаторів (типово 70)\n"
        "  --leap-at SEC    увести секунду координації на цій секунді прогону\n"
        "  --rollover       почати за 30 с до переповнення лічильника тижнів\n", argv0);
}

std::expected<Config, std::string> parse_args(std::span<char* const> args)
{
    Config c;
    for (std::size_t i = 1; i < args.size(); ++i) {
        const std::string_view key{args[i]};
        const bool needs_value = key != "--rollover";
        if (needs_value && i + 1 >= args.size())
            return std::unexpected(std::format("{}: бракує значення", key));
        const std::string value = needs_value ? args[++i] : std::string{};
        const auto number = [&] { return std::strtod(value.c_str(), nullptr); };

        if      (key == "--rinex")     c.rinex = value;
        else if (key == "--port")      c.port = value;
        else if (key == "--out")       c.out = value;
        else if (key == "--sec")       c.seconds = number();
        else if (key == "--lat")       c.lat_deg = number();
        else if (key == "--lon")       c.lon_deg = number();
        else if (key == "--alt")       c.alt_m = number();
        else if (key == "--speed")     c.speed_ms = number();
        else if (key == "--course")    c.heading_deg = number();
        else if (key == "--mp-height") c.mp_height = number();
        else if (key == "--mp-gamma")  c.mp_gamma = number();
        else if (key == "--fixed-pad") c.fixed_pad_db = number();
        else if (key == "--leap-at")   c.leap_at = number();
        else if (key == "--rollover")  c.rollover = true;
        else return std::unexpected(std::format("невідомий ключ {}", key));
    }

    if (c.rinex.empty() || c.port.empty()) return std::unexpected("потрібні --rinex і --port");
    if (c.mp_gamma < 0.0 || c.mp_gamma > 1.0)
        return std::unexpected("коефіцієнт відбиття має бути в межах 0..1");
    return c;
}

struct Emission {
    SatelliteState state;
    double range{};
};

// Час випромінювання шукається ітераційно: затримка залежить від дистанції,
// а дистанція — від того, де супутник був у момент випромінювання.
std::optional<Emission> solve_emission(const Ephemeris& eph, GpsTime t_rx, const Vec3& user)
{
    double tau = 0.075;                       // грубе перше наближення, ~70 мс
    Emission result;

    for (int i = 0; i < 4; ++i) {
        const auto raw = eph.state_at(t_rx + (-tau));
        if (!raw) return std::nullopt;

        // Поправка Саньяка: поки хвиля летіла, система координат оберталася.
        SatelliteState rotated = *raw;
        rotated.position = rotate_earth(raw->position, tau);
        rotated.velocity = rotate_earth(raw->velocity, tau);

        const double range = (rotated.position - user).norm();
        const double tau_next = range / kSpeedOfLight - raw->clock_bias;

        result = {rotated, range};
        if (std::abs(tau_next - tau) < 1e-12) break;
        tau = tau_next;
    }
    return result;
}

int run(const Config& cfg)
{
    auto nav = Navigation::load(cfg.rinex);
    if (!nav) {
        std::cerr << std::format("{}: {}\n", cfg.rinex, describe(nav.error()));
        return 1;
    }
    if (!nav->ionosphere())
        std::cerr << "у шапці немає GPSA/GPSB — іоносферу моделювати нічим, буде нуль\n";

    GpsTime t{nav->all().front().week, nav->all().front().toe};
    if (cfg.rollover) {
        t = GpsTime{(t.week() / 1024) * 1024 + 1023, kSecondsPerWeek - 30.0};
        std::cerr << std::format("сценарій переповнення: старт на тижні {} (у кадрі {})\n",
                                 t.week(), t.broadcast_week());
        // Ефемериди переносимо на той самий тиждень, інакше вони протермінуються.
        for (auto& e : nav->all()) { e.week = t.week(); e.toe = t.tow() + 15.0; }
    }

    NavContext ctx;
    if (const auto& iono = nav->ionosphere()) { ctx.alpha = iono->alpha(); ctx.beta = iono->beta(); }
    ctx.leap.current = nav->leap_seconds().value_or(18);
    ctx.leap.future  = ctx.leap.current;

    Geodetic llh{cfg.lat_deg * kPi / 180.0, cfg.lon_deg * kPi / 180.0, cfg.alt_m};
    Vec3 user_pos = to_ecef(llh);
    const Vec3 user_vel = enu_vector(llh,
                                     cfg.speed_ms * std::sin(cfg.heading_deg * kPi / 180.0),
                                     cfg.speed_ms * std::cos(cfg.heading_deg * kPi / 180.0),
                                     0.0);

    auto attenuator = Attenuator::connect(cfg.port);
    if (!attenuator) {
        std::cerr << std::format("атенюатор: {}\n", attenuator.error());
        return 1;
    }

    std::ofstream file;
    if (cfg.out != "-") {
        file.open(cfg.out, std::ios::binary);
        if (!file) { std::cerr << std::format("{}: не відкривається\n", cfg.out); return 1; }
    }
    std::ostream& out = file.is_open() ? file : std::cout;

    Synthesizer synth{kSampleRateSps, kDacScale};
    std::vector<std::int16_t> iq(2 * kSamplesPerEpoch);

    const long total_epochs = static_cast<long>(cfg.seconds / kEpochSeconds);
    double user_clock_bias = 0.0;
    double strongest_dbm = kZenithRxDbm;
    bool leap_done = false;
    int last_week = t.broadcast_week();

    for (long epoch = 0; epoch < total_epochs && g_stop == 0; ++epoch) {
        const double model_time = static_cast<double>(epoch) * kEpochSeconds;

        if (epoch % kGeometryEvery == 0) {
            strongest_dbm = -200.0;

            for (int prn = 1; prn <= 32; ++prn) {
                const Ephemeris* eph = nav->select(prn, t);
                if (eph == nullptr) { synth.release(prn); continue; }

                const auto emission = solve_emission(*eph, t, user_pos);
                if (!emission) { synth.release(prn); continue; }

                const LineOfSight los = line_of_sight(user_pos, llh, emission->state.position);
                if (los.elevation < kElevationMask) { synth.release(prn); continue; }

                const double iono = nav->ionosphere()
                                  ? nav->ionosphere()->delay_s(llh, los, t.tow()) : 0.0;
                const double trop = troposphere_delay_s(llh, los.elevation, cfg.humidity);

                // Повна псевдовідстань: геометрія, розбіжність годинників, атмосфера.
                const double pseudorange = emission->range
                    + kSpeedOfLight * (user_clock_bias - emission->state.clock_bias)
                    + kSpeedOfLight * (iono + trop);

                // Хід годинників теж зсуває частоту: швидший бортовий стандарт
                // випромінює вище, повільніший приймач бачить це як зсув.
                const double doppler = doppler_hz(los, user_vel, emission->state.velocity, kL1Hz)
                    + kL1Hz * (emission->state.clock_drift - cfg.clock_drift_ppb * 1e-9);

                const double power = kZenithRxDbm
                    + (rx_antenna_gain_db(los.elevation) - rx_antenna_gain_db(kPi / 2.0))
                    - (free_space_loss_db(emission->range, kL1Hz)
                       - free_space_loss_db(kNominalRangeM, kL1Hz));
                strongest_dbm = std::max(strongest_dbm, power);

                const auto multipath = Multipath::from_geometry(cfg.mp_height, los.elevation,
                                                                cfg.mp_gamma);
                const GpsTime t_tx = t + (-pseudorange / kSpeedOfLight);

                Channel& channel = synth.acquire(prn);
                channel.ensure_frame(*eph, ctx, t_tx);
                channel.update(t_tx, pseudorange, doppler, power, los.elevation, multipath);
            }

            if (synth.size() < 4)
                std::cerr << std::format("t={:.1f} с: над горизонтом лише {} апаратів — "
                                         "рішення не буде\n", model_time, synth.size());
        }

        // Крайова подія: уведення секунди координації.
        if (cfg.leap_at >= 0.0 && !leap_done && model_time >= cfg.leap_at) {
            ctx.leap.future = ctx.leap.current + 1;
            ctx.leap.wn_lsf = t.broadcast_week() & 0xFF;
            ctx.leap.dn = static_cast<int>(t.tow() / 86400.0) + 1;
            synth.invalidate_frames();
            std::cerr << std::format("t={:.1f} с: у кадр піде ΔtLSF={} (WNLSF={}, DN={})\n",
                                     model_time, ctx.leap.future, ctx.leap.wn_lsf, ctx.leap.dn);
            leap_done = true;
        }

        if (t.broadcast_week() != last_week) {
            std::cerr << std::format("t={:.1f} с: лічильник тижнів у кадрі {} → {} (повний {})\n",
                                     model_time, last_week, t.broadcast_week(), t.week());
            last_week = t.broadcast_week();
            synth.invalidate_frames();
        }

        synth.generate(iq);
        out.write(reinterpret_cast<const char*>(iq.data()),
                  static_cast<std::streamsize>(iq.size() * sizeof(std::int16_t)));
        if (!out) { std::cerr << "запис I/Q обірвався\n"; break; }

        // Атенюатор ведеться за найсильнішим апаратом: рівень на вході приймача
        // тримаємо штатним, скільки б не змінювалася дистанція.
        if (epoch % kAttenuatorEvery == 0) {
            const double needed = kSdrOutputDbm - strongest_dbm;
            double programmable = needed - cfg.fixed_pad_db;
            if (programmable < 0.0) {
                std::cerr << std::format("потрібно {:.1f} дБ, а фіксований каскад дає {:.1f} — "
                                         "доберіть атенюатори!\n", needed, cfg.fixed_pad_db);
                programmable = 0.0;
            }
            (void)attenuator->request(std::min(programmable, kMaxAttenuationDb));
        }
        attenuator->poll();
        if (attenuator->failed()) {
            std::cerr << "керування рівнем втрачено — зупиняємось, доки не спалили LNA\n";
            break;
        }

        t += kEpochSeconds;
        user_pos = user_pos + user_vel * kEpochSeconds;
        llh = to_geodetic(user_pos);
        user_clock_bias += cfg.clock_drift_ppb * 1e-9 * kEpochSeconds;
    }

    std::cerr << std::format("завершено: каналів {}, обрізаних вибірок {}, "
                             "команд SCPI {}, тайм-аутів {}\n",
                             synth.size(), synth.clipped(),
                             attenuator->commands(), attenuator->timeouts());
    return 0;
}

}  // namespace

int main(int argc, char** argv)
{
    const auto cfg = parse_args(std::span{argv, static_cast<std::size_t>(argc)});
    if (!cfg) {
        std::cerr << cfg.error() << '\n';
        usage(argv[0]);
        return 2;
    }

    std::signal(SIGINT, on_sigint);
    return run(*cfg);
}
