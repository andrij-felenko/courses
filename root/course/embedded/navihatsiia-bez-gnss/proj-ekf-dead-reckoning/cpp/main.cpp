// main.cpp — прогін навігаційного модуля на синтетичному польоті.
//
// На апараті цього файла немає: там ті самі виклики роблять дві задачі
// FreeRTOS — високопріоритетна за перериванням готовності IMU (500 Гц) і
// фонова задача давачів (50 Гц потік, 20 Гц далекомір). Тут вони зведені в
// один цикл, щоб було видно час і порядок подій.
//
// Прогін показує те, заради чого фільтр і будувався: як швидко відлітає
// чиста інерціальна навігація і скільки з цього відльоту знімають оптичний
// потік, далекомір і ZUPT. Істина відома точно, тому похибку тут не
// вгадують, а рахують.

#include "ekf.hpp"
#include "optical_flow.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <deque>
#include <format>
#include <iostream>
#include <numbers>
#include <optional>
#include <random>
#include <utility>
#include <variant>

// Vec3 і Mat3 — це псевдоніми std::array, тому пошук операторів за
// аргументами (ADL) привів би в namespace std, а не в nav. Одна директива
// тут дешевша за обгортання масивів у власні типи заради самого пошуку.
using namespace nav;

namespace {

constexpr float kDt = 0.002f;              // 500 Гц — крок IMU
constexpr std::uint32_t kDtUs = 2000;
constexpr std::uint32_t kSteps = 30000;    // 60 секунд
constexpr std::uint32_t kFlowEvery = 10;   // 50 Гц
constexpr std::uint32_t kRangeEvery = 25;  // 20 Гц
constexpr std::uint32_t kFlowLatencyUs = 20000;   // кадр описує момент 20 мс тому
constexpr std::uint32_t kRangeLatencyUs = 5000;
constexpr std::uint32_t kReportEvery = 2500;      // рядок звіту раз на 5 с

// Паспортна стала PMW3901, та сама, що в модулі потоку. Якби вони
// розійшлися, фільтр дістав би систематичний масштабний коефіцієнт у
// швидкості — це і є найчастіша причина «потік недооцінює швидкість».
constexpr float kRadPerPixel = static_cast<float>(42.0 * std::numbers::pi / 180.0 / 35.0);

// Шуми давачів — приблизно рівень ICM-42688 і PMW3901.
constexpr float kAccNoise = 0.06f;    // м/с²
constexpr float kGyroNoise = 0.003f;  // рад/с
constexpr float kFlowNoise = 0.35f;   // пікселів на кадр
constexpr float kRangeNoise = 0.012f; // м

// ── Істина ──────────────────────────────────────────────────────────────
// Дві ділянки польоту, розділені зупинками. Переходи згладжені, щоб
// прискорення лишалося скінченним: стрибок швидкості означав би нескінченне
// прискорення, а акселерометр такого не показав би. Зупинки тут не для
// краси — без них не видно ні детектора нерухомості, ні того, як ZUPT
// витягує зсув нуля акселерометра.

float smoothstep(float a, float b, float t) noexcept
{
    if (t <= a) return 0.0f;
    if (t >= b) return 1.0f;
    const float x = (t - a) / (b - a);
    return x * x * (3.0f - 2.0f * x);
}

float motionGate(float t) noexcept
{
    const float leg1 = smoothstep(4.0f, 5.5f, t) * (1.0f - smoothstep(22.5f, 24.0f, t));
    const float leg2 = smoothstep(30.0f, 31.5f, t) * (1.0f - smoothstep(52.5f, 54.0f, t));
    return leg1 + leg2;
}

Vec3 velocityProfile(float t) noexcept
{
    const float g = motionGate(t);
    return {g * (1.20f + 0.40f * std::sin(0.25f * t)),
            g * (0.60f * std::sin(0.15f * t)),
            g * (0.15f * std::sin(0.50f * t))};
}

Vec3 attitudeProfile(float t) noexcept
{
    const float g = motionGate(t);
    return {g * 0.12f * std::sin(0.70f * t),           // крен
            g * 0.09f * std::sin(0.50f * t + 1.0f),    // тангаж
            g * 0.30f * std::sin(0.10f * t)};          // курс
}

// R = Rz(курс)·Ry(тангаж)·Rx(крен) — класичний порядок для NED.
Mat3 rpyToMatrix(Vec3 const& rpy) noexcept
{
    const float cr = std::cos(rpy[0]), sr = std::sin(rpy[0]);
    const float cp = std::cos(rpy[1]), sp = std::sin(rpy[1]);
    const float cy = std::cos(rpy[2]), sy = std::sin(rpy[2]);

    return Mat3{Vec3{cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr},
                Vec3{sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr},
                Vec3{-sp, cp * sr, cp * cr}};
}

// Кутова швидкість тіла з похідної матриці повороту: Ω = Rᵀ·Ṙ —
// кососиметрична, і з неї прямо читаються p, q, r. Числова похідна дешевша
// й надійніша за виведення формул переходу від похідних кутів Ейлера, а
// точності 1e-4 с вистачає з великим запасом.
Vec3 gyroAt(float t) noexcept
{
    constexpr float h = 1.0e-4f;
    const Mat3 Ra = rpyToMatrix(attitudeProfile(t - h));
    const Mat3 Rb = rpyToMatrix(attitudeProfile(t + h));
    const Mat3 Rt = rpyToMatrix(attitudeProfile(t));

    Mat3 Rdot{};
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) Rdot[i][j] = (Rb[i][j] - Ra[i][j]) / (2.0f * h);
    }

    const Mat3 omega = transpose(Rt) * Rdot;
    return {omega[2][1], omega[0][2], omega[1][0]};
}

// Модель світу разом з давачами. Кожен «замір» — точна обернена дія до
// того, що робить відповідний модуль навігації: IMU повертає прискорення в
// систему тіла й додає гравітацію назад, потік перетворює швидкість на
// пікселі, доклавши обертання.
class World {
public:
    explicit World(std::uint32_t seed) : rng_{seed}
    {
        pos_[2] = -1.5f;                 // старт на висоті 1.5 м (вісь Z вниз)
        evaluate(0.0f);
    }

    void step(float dt) noexcept
    {
        const Vec3 vOld = vel_;
        evaluate(t_ + dt);
        for (std::size_t i = 0; i < 3; ++i) pos_[i] += 0.5f * (vOld[i] + vel_[i]) * dt;
    }

    float time() const noexcept { return t_; }
    float height() const noexcept { return -pos_[2]; }
    Vec3 const& position() const noexcept { return pos_; }
    Mat3 const& attitude() const noexcept { return Rwb_; }
    Vec3 const& accBias() const noexcept { return accBias_; }

    // {питома сила в системі тіла, кутові швидкості} — усе зі зсувом і шумом.
    std::pair<Vec3, Vec3> readImu()
    {
        Vec3 aWorld = acc_;
        aWorld[2] -= nav::Ekf::kGravity;   // акселерометр міряє питому силу

        Vec3 aBody = transpose(Rwb_) * aWorld;
        Vec3 gyro{};
        for (std::size_t i = 0; i < 3; ++i) {
            aBody[i] += accBias_[i] + kAccNoise * gauss_(rng_);
            gyro[i] = gyro_[i] + gyroBias_[i] + kGyroNoise * gauss_(rng_);
        }
        return {aBody, gyro};
    }

    nav::FlowFrame readFlow(float dtFrame)
    {
        ++flowFrames_;

        const float d = std::max(height(), 0.05f);
        const Vec3 vBody = transpose(Rwb_) * vel_;

        // Обернена деротація: до поступальної складової додаємо ту, що її
        // створює обертання апарата. Модуль потоку робитиме зворотне.
        const float wx = vBody[0] / d + gyro_[1];
        const float wy = vBody[1] / d - gyro_[0];

        float px = wx * dtFrame / kRadPerPixel + kFlowNoise * gauss_(rng_);
        float py = wy * dtFrame / kRadPerPixel + kFlowNoise * gauss_(rng_);

        std::uint8_t squal = 120;

        // Кожен 137-й кадр — поверхня без текстури (свіжий асфальт, вода).
        // Сенсор чесно попереджає низьким SQUAL: кадр має бути відкинутий ще
        // до фільтра.
        if (flowFrames_ % 137 == 0) squal = 12;

        // Кожен 331-й — відблиск або змаз: якість висока, числа брехливі.
        // Ось цей випадок ловить уже тільки строб Махаланобіса.
        if (flowFrames_ % 331 == 0) {
            px *= 6.0f;
            py *= -4.0f;
        }

        return nav::FlowFrame{.dpx = static_cast<std::int16_t>(std::lround(px)),
                              .dpy = static_cast<std::int16_t>(std::lround(py)),
                              .squal = squal,
                              .dt = dtFrame,
                              .gyro = gyro_,
                              .Rwb = Rwb_,
                              .rangeRaw = readRange()};
    }

    float readRange()
    {
        ++rangeReads_;

        const float tiltCos = Rwb_[2][2];
        float range = height() / std::max(tiltCos, 0.1f);
        range += kRangeNoise * gauss_(rng_);

        // Кожне 211-те читання — промінь спіймав кущ: дальність різко менша.
        if (rangeReads_ % 211 == 0) range *= 0.45f;
        return range;
    }

private:
    void evaluate(float t) noexcept
    {
        Rwb_ = rpyToMatrix(attitudeProfile(t));
        gyro_ = gyroAt(t);
        vel_ = velocityProfile(t);

        constexpr float h = 1.0e-3f;
        const Vec3 va = velocityProfile(t - h);
        const Vec3 vb = velocityProfile(t + h);
        for (std::size_t i = 0; i < 3; ++i) acc_[i] = (vb[i] - va[i]) / (2.0f * h);

        t_ = t;
    }

    float t_{};
    Vec3 pos_{}, vel_{}, acc_{}, gyro_{};
    Mat3 Rwb_{};

    // Систематичні похибки давачів, які фільтр має вивести сам. Зсув
    // гіроскопа в стан не входить: він псує орієнтацію, а не швидкість.
    Vec3 accBias_{0.06f, -0.04f, 0.03f};
    Vec3 gyroBias_{0.002f, -0.001f, 0.0015f};

    std::mt19937 rng_;
    std::normal_distribution<float> gauss_{0.0f, 1.0f};
    std::uint32_t flowFrames_{};
    std::uint32_t rangeReads_{};
};

// ── Детектор нерухомості ────────────────────────────────────────────────
// Умова стоянки — модуль питомої сили близький до g І кутова швидкість мала,
// і так протягом усього вікна. Одного відліку мало: у момент зміни напрямку
// руху прискорення теж проходить через g, а вікно в 128 мс такий проліт
// відсіює.
class Stillness {
public:
    bool update(Vec3 const& aBody, Vec3 const& gyro) noexcept
    {
        const auto norm = [](Vec3 const& v) {
            return std::sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
        };

        window_.push_back({norm(aBody), norm(gyro)});
        if (window_.size() > kWindow) window_.pop_front();
        if (window_.size() < kWindow) return false;

        for (auto const& [accMag, gyroMag] : window_) {
            if (std::fabs(accMag - nav::Ekf::kGravity) > 0.30f) return false;
            if (gyroMag > 0.05f) return false;
        }
        return true;
    }

private:
    struct Sample { float accMag, gyroMag; };
    static constexpr std::size_t kWindow = 64;   // ≈128 мс при 500 Гц
    std::deque<Sample> window_;
};

// ── Компенсація затримки вимірювань ─────────────────────────────────────
// Кадр потоку описує момент, який уже минув: поки кадр знято, приїхало по
// SPI й оброблено, апарат устиг змінити швидкість. Влити таке вимірювання в
// поточний стан означає систематично тягнути оцінку назад.
//
// Дешевий і чесний спосіб — перенести саме ВИМІРЮВАННЯ вперед: фільтр знає,
// на скільки він змінив швидкість і координату відтоді, і рівно ці прирости
// треба додати до запізнілого числа.
//
// PX4 і ArduPilot роблять строгіший варіант тієї самої думки: у буфері там
// лежать цілі стани фільтра, корекція застосовується заднім числом до
// історичного зрізу, а вперед переінтегровується весь буфер. Точніше на
// різких маневрах і дорожче за пам'яттю та часом.
class DelayHistory {
public:
    void push(std::uint32_t tUs, Vec3 const& dv, Vec3 const& dp)
    {
        history_.push_back({tUs, dv, dp});
        if (history_.size() > kWindow) history_.pop_front();
    }

    // Сумарні прирости від моменту tMeasUs і дотепер.
    std::pair<Vec3, Vec3> since(std::uint32_t tMeasUs) const noexcept
    {
        Vec3 dv{}, dp{};
        for (auto it = history_.rbegin(); it != history_.rend(); ++it) {
            if (it->tUs <= tMeasUs) break;
            for (std::size_t i = 0; i < 3; ++i) {
                dv[i] += it->dv[i];
                dp[i] += it->dp[i];
            }
        }
        return {dv, dp};
    }

private:
    struct Entry { std::uint32_t tUs; Vec3 dv, dp; };
    static constexpr std::size_t kWindow = 64;   // 128 мс запасу при 500 Гц
    std::deque<Entry> history_;
};

// ── Публікація стану для контуру керування ──────────────────────────────
// Оцінку читає задача PID, а пише її задача IMU з вищим пріоритетом і правом
// перервати читача посеред структури. Мьютекс тут заборонений:
// високопріоритетна задача не має права чекати на низькопріоритетну.
//
// Класичний вихід — seqlock. Писар піднімає лічильник до непарного, кладе
// дані, піднімає до парного. Читач бачить непарний лічильник або його зміну
// під час читання — і просто читає ще раз. Писар не блокується ніколи, читач
// у найгіршому разі повторює кілька тактів.
class StatePublisher {
public:
    struct Snapshot {
        std::uint32_t tUs{};
        Vec3 pos{};
        Vec3 vel{};
        float sigmaPos{};
    };

    void publish(Snapshot const& s) noexcept
    {
        const std::uint32_t seq = seq_.load(std::memory_order_relaxed);
        seq_.store(seq + 1, std::memory_order_relaxed);       // непарний
        std::atomic_thread_fence(std::memory_order_release);

        data_ = s;

        std::atomic_thread_fence(std::memory_order_release);
        seq_.store(seq + 2, std::memory_order_relaxed);       // парний
    }

    // nullopt — нас переривали чотири рази поспіль; читач бере старий знімок.
    std::optional<Snapshot> read() const noexcept
    {
        for (int attempt = 0; attempt < 4; ++attempt) {
            const std::uint32_t before = seq_.load(std::memory_order_relaxed);
            if (before & 1u) continue;                        // писар у структурі
            std::atomic_thread_fence(std::memory_order_acquire);

            Snapshot copy = data_;

            std::atomic_thread_fence(std::memory_order_acquire);
            if (seq_.load(std::memory_order_relaxed) == before) return copy;
        }
        return std::nullopt;
    }

private:
    std::atomic<std::uint32_t> seq_{0};
    Snapshot data_{};
};

// ── Черга «сенсор → навігація» ──────────────────────────────────────────
// Вимірювання не з'являється в обробнику миттєво. Затримку відтворюємо явно
// — інакше половина роботи компенсації лишилася б непоказаною.

struct RangeSample {
    float rangeRaw{};
    Mat3 Rwb{};
};

struct Pending {
    std::uint32_t deliverUs{};   // коли доїде до задачі
    std::uint32_t tUs{};         // момент, ЯКИЙ воно описує
    std::variant<nav::FlowFrame, RangeSample> payload;
};

template <class... Ts> struct overloaded : Ts... { using Ts::operator()...; };
template <class... Ts> overloaded(Ts...) -> overloaded<Ts...>;

}  // namespace

int main()
{
    World world{20240917u};
    nav::Ekf ekf;                 // повний фільтр із корекціями
    nav::Ekf inertial;            // та сама механіка, але без жодної корекції
    nav::OpticalFlow flow;
    Stillness stillness;
    DelayHistory history;
    StatePublisher publisher;
    std::deque<Pending> queue;

    // Обидва фільтри стартують із правильної позиції: далі розходження — це
    // вже тільки робота давачів.
    ekf.setDown(world.position()[2]);
    inertial.setDown(world.position()[2]);

    std::uint32_t flowFused = 0, flowDropped = 0, rangeFused = 0, zupts = 0;
    std::uint32_t tUs = 0;

    std::cout << "  t,с | висота |  похибка позиції, м  | оцінка зсуву акс., м/с²  | σ_pos\n"
                 "      |    м   |  фільтр    інерція   |   x       y       z      |   м\n"
                 "------+--------+----------------------+--------------------------+-------\n";

    for (std::uint32_t step = 0; step < kSteps; ++step, tUs += kDtUs) {
        world.step(kDt);

        // ── Задача IMU, 500 Гц, найвищий пріоритет ──
        auto const [aBody, gyro] = world.readImu();

        const Vec3 posBefore = ekf.position();
        const Vec3 velBefore = ekf.velocity();

        if (!ekf.predict(aBody, world.attitude(), kDt)) {
            // На апараті сюди потрапляють збійні відліки IMU; крок пропущено,
            // наступний просто прийде з більшим dt.
            continue;
        }
        inertial.predict(aBody, world.attitude(), kDt);

        Vec3 dv{}, dp{};
        const Vec3 posAfter = ekf.position();
        const Vec3 velAfter = ekf.velocity();
        for (std::size_t i = 0; i < 3; ++i) {
            dv[i] = velAfter[i] - velBefore[i];
            dp[i] = posAfter[i] - posBefore[i];
        }
        history.push(tUs, dv, dp);

        // Детектор нерухомості й ZUPT. Строб усередині фільтра лишає за
        // собою останнє слово, якщо детектор помилився.
        const bool stationary = stillness.update(aBody, gyro);
        if (stationary && step % 25 == 0) {          // 20 Гц вистачає
            if (ekf.updateZupt(0.0025f)) ++zupts;
        }

        // ── Задача давачів: кадри лягають у чергу із затримкою ──
        if (step % kFlowEvery == 0) {
            queue.push_back({.deliverUs = tUs + kFlowLatencyUs,
                             .tUs = tUs,
                             .payload = world.readFlow(kDt * static_cast<float>(kFlowEvery))});
        }
        if (step % kRangeEvery == 0) {
            queue.push_back({.deliverUs = tUs + kRangeLatencyUs,
                             .tUs = tUs,
                             .payload = RangeSample{.rangeRaw = world.readRange(),
                                                    .Rwb = world.attitude()}});
        }

        // ── Те, що вже доїхало, зливаємо ──
        while (!queue.empty() && queue.front().deliverUs <= tUs) {
            const Pending item = queue.front();
            queue.pop_front();

            auto const [backDv, backDp] = history.since(item.tUs);

            std::visit(overloaded{
                [&](nav::FlowFrame const& frame) {
                    auto meas = flow.measure(frame);
                    if (!meas) {
                        ++flowDropped;
                        return;
                    }

                    // Вимірювання описує швидкість у минулому — переносимо
                    // його вперед на приріст, який фільтр устиг накрутити.
                    const float vx = meas->vx + backDv[0];
                    const float vy = meas->vy + backDv[1];

                    // Строб 4.0 — це 2σ за χ² з одним ступенем вільності.
                    if (ekf.updateVelocity2d(vx, vy, meas->r, 4.0f)) ++flowFused;
                    else ++flowDropped;
                },
                [&](RangeSample const& sample) {
                    const float tiltCos = sample.Rwb[2][2];
                    if (!(tiltCos > 0.70f)) return;

                    // Дальність уздовж променя × косинус нахилу = висота;
                    // у NED вона від'ємна (вісь Z вниз).
                    const float pz = -(sample.rangeRaw * tiltCos) + backDp[2];
                    const float r = 0.0004f + 0.01f * sample.rangeRaw * sample.rangeRaw;

                    if (ekf.updateAltitude(pz, r, 4.0f)) ++rangeFused;
                }}, item.payload);
        }

        // Свіжу оцінку віддаємо контуру керування. На апараті це кінець
        // обробника переривання IMU: далі стан читає задача PID.
        publisher.publish({.tUs = tUs,
                           .pos = ekf.position(),
                           .vel = ekf.velocity(),
                           .sigmaPos = ekf.posSigma(0)});

        // ── Звіт: читаємо так само, як його читав би контур керування ──
        if (step % kReportEvery == 0) {
            const auto snapshot = publisher.read();
            if (!snapshot) continue;

            const Vec3 pos = snapshot->pos;
            const Vec3 posInertial = inertial.position();
            const Vec3 bias = ekf.bias();

            float err = 0.0f, errInertial = 0.0f;
            for (std::size_t i = 0; i < 3; ++i) {
                const float d1 = pos[i] - world.position()[i];
                const float d2 = posInertial[i] - world.position()[i];
                err += d1 * d1;
                errInertial += d2 * d2;
            }

            std::cout << std::format("{:5.1f} | {:6.2f} | {:8.2f} {:10.2f} | "
                                     "{:7.3f} {:7.3f} {:7.3f} | {:5.2f}{}\n",
                                     world.time(), world.height(),
                                     std::sqrt(err), std::sqrt(errInertial),
                                     bias[0], bias[1], bias[2],
                                     snapshot->sigmaPos, stationary ? "  [стоїмо]" : "");
        }
    }

    auto const& rej = flow.rejections();
    auto const& stats = ekf.stats();

    std::cout << std::format("\nІстинний зсув акселерометра: {:.3f} {:.3f} {:.3f} м/с²\n",
                             world.accBias()[0], world.accBias()[1], world.accBias()[2]);
    std::cout << std::format("Кадрів потоку злито {}, відкинуто {} "
                             "(якість {}, змаз {}, дальність {}, нахил {})\n",
                             flowFused, flowDropped, rej.quality, rej.rate, rej.range, rej.tilt);
    std::cout << std::format("Далекомір злито {}, ZUPT {}, строб фільтра відкинув {}, "
                             "чисельних відмов {}\n",
                             rangeFused, zupts, stats.gated, stats.numeric);
    std::cout << std::format("Коваріацію рятувала гігієна {} разів\n", stats.healed);

    return 0;
}
