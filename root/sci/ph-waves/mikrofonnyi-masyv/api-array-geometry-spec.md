# 📋 Специфікація геометрії та векторів рулювання масивів

У цій специфікації наведено стандартизовані математичні моделі просторових координат, розрахунку векторів рулювання (steering vectors), граничних частот просторового аліасингу, вікон аподизації та структури даних для конфігурації акустичних мікрофонних масивів різної топології.

Документ визначає програмний контракт для модулів просторової обробки акустичних сигналів, узгоджуючи формати представлення положення капсулів, параметри звукового середовища та структури для формування діаграм спрямованості у часовій і частотній областях.

## 1. Системи координат та топології масивів

Положення кожного `m`-го мікрофона (`m = 0, ..., M - 1`) у тривимірному просторі задається радіус-вектором у правосторонній декартовій системі координат:

```
\vec{r}_m = [x_m, y_m, z_m]^T  (у метрах)
```

Початок координат `(0, 0, 0)` зазвичай обирається у геометричному центрі ваги (центроїді) масиву або на першому опорному сенсорі `M₀`.

Напрямок приходу плоскої акустичної хвилі з далекого поля визначається одиничним вектором поширення `\vec{u}(\theta, \varphi)`:
- `\theta` — азимутальний кут (azimuth) у горизонтальній площині `XY`, вимірюваний від осі `Y` за годинниковою стрілкою або від нормалі до масиву (`\theta \in [-180°, +180°]` або `[-90°, +90°]`);
- `\varphi` — кут місця / елевація (elevation) над площиною `XY` (`\varphi \in [-90°, +90°]`, де 0° відповідає горизонту, а +90° — зеніту).

Одиничний вектор напрямку поширення записується через тригонометричні проекції:

```
\vec{u}(\theta, \varphi) = [sin(\theta) · cos(\varphi),  cos(\theta) · cos(\varphi),  sin(\varphi)]^T
```

### Порівняльний аналіз топологій масивів

Вибір просторового розташування сенсорів визначає функціональні можливості системи:

1. **1D Однорідний лінійний масив (Uniform Linear Array, ULA):**
   Сенсори розміщені вздовж осі `X` з рівномірним кроком: `x_m = m · d`, `y_m = 0`, `z_m = 0`. Ця геометрія забезпечує найвищу кутову роздільну здатність за азимутом при мінімальній кількості каналів обробки. Проте лінійний масив має непереборну осьову дзеркальну симетрію: затримка сигналу є абсолютно однаковою для кутів `θ` та `180° - θ`, утворюючи так званий конус невизначеності. Тому лінійні масиви застосовують виключно тоді, коли задня півсфера акустично екранована корпусом приладу (телевізори, саундбари, панелі приладів).

2. **2D Однорідний кільцевий масив (Uniform Circular Array, UCA):**
   Сенсори розташовані по колу радіуса `R`: `x_m = R · cos(2π m / M)`, `y_m = R · sin(2π m / M)`, `z_m = 0`. Кільцева топологія усуває дзеркальну неоднозначність і забезпечує повний круговий огляд 360° у горизонтальній площині. Ширина головної пелюстки діаграми спрямованості залишається практично незмінною при будь-якому азимутальному куті приходу звуку, що робить UCA стандартом для смарт-колонок і круглих конференц-систем.

3. **2D Матричний прямокутний масив (Uniform Rectangular Array, URA):**
   Сенсори розміщені на площині у вигляді прямокутної сітки `M_x × M_y`: `x_{p,q} = p · d_x`, `y_{p,q} = q · d_y`, `z_{p,q} = 0`. Завдяки двом незалежним просторовим осям дискретизації масив дозволяє керувати променем як за азимутом, так і за кутом місця (елевацією). Це необхідно для систем тривимірного акустичного трекінгу та акустичних камер.

4. **3D Сферичний масив (Spherical Microphone Array):**
   Сенсори розміщуються на поверхні жорсткої або відкритої сфери радіуса `R`. Застосування сферичного розкладу поля за сферичними гармоніками (Spherical Harmonics / Ambisonics) забезпечує повну просторову ізотропію у тілесному куті `4π` стерадіан без сліпих зон.

## 2. Специфікація вектора рулювання (Steering Vector)

Вектор рулювання `\vec{v}(f, \theta, \varphi)` є частотно-просторовою передавальною характеристикою масиву, що описує фазовий стан акустичного поля на всіх сенсорах для гармонічної складової частоти `f` (з довжиною хвилі `\lambda = c / f`), що надходить з кутового напрямку `(\theta, \varphi)`.

Геометрична різниця ходу хвилі між `m`-м мікрофоном та початком координат становить:

```
\Delta r_m(\theta, \varphi) = \vec{r}_m \cdot \vec{u}(\theta, \varphi) = x_m · sin(\theta)·cos(\varphi) + y_m · cos(\theta)·cos(\varphi) + z_m · sin(\varphi)
```

Відповідна фізична часова затримка приходу:

```
\tau_m(\theta, \varphi) = \Delta r_m(\theta, \varphi) / c
```

Фазовий набіг на частоті `f` (де `k = 2\pi f / c` — хвильове число):

```
\Delta \phi_m(f, \theta, \varphi) = 2\pi f · \tau_m(\theta, \varphi) = k · \Delta r_m(\theta, \varphi)
```

Комплексний вектор просторового рулювання розмірності `M × 1`:

```
\vec{v}(f, \theta, \varphi) = [e^{-j \Delta \phi_0},  e^{-j \Delta \phi_1},  ...,  e^{-j \Delta \phi_{M-1}}]^T
```

У матричному вигляді для широкосмугових сигналів вектор рулювання розраховується для кожного частотного біна `f_k = k · f_s / N`.

## 3. Граничні частоти просторового аліасингу

Просторовий аліасинг виникає, коли просторовий період дискретизації хвильового поля `d` перевищує половину довжини звукової хвилі. При цьому фазовий зсув між сусідніми мікрофонами перевищує `π` радіан, що призводить до виникнення хибних головних пелюсток (ґраткових пелюсток, grating lobes).

Критерій просторової дискретизації Найквіста:

```
d_max \le \lambda_min / 2 = c / (2 · f_max)
```

Гранична частота однозначної пеленгації без аліасингу:

```
f_alias = c / (2 · d_max)
```

Якщо робочий діапазон частот перевищує `f_alias`, масив фіксуватиме хибні джерела звуку в напрямках нульових значень знаменника характеристичної функції масиву.

Розрахунок граничних частот для типових конструктивних кроків сенсорів у повітрі (`c = 343 м/с`):
- При кроці `d = 10 мм` гранична частота становить `17 150 Гц`, що повністю перекриває чутний діапазон високоякісного аудіо.
- При кроці `d = 21 мм` гранична частота дорівнює `8 167 Гц`, що ідеально підходить для широкосмугової телефонії HD Voice (стандарт G.722).
- При кроці `d = 42.8 мм` гранична частота становить `4 007 Гц`, що достатньо для класичного телефонного каналу мови (300–3400 Гц).
- При кроці `d = 85.7 мм` гранична частота знижується до `2 001 Гц`, що оптимізовано для виявлення низькочастотних шумів двигунів внутрішнього згоряння та безпілотників.

## 4. Вікна просторової аподизації (Spatial Windowing)

Для керування формою просторової діаграми спрямованості та придушення бічних пелюсток сигнали мікрофонних каналів множаться на вагові коефіцієнти аподизації `w_m`. Плавне зменшення чутливості від центральних елементів масиву до крайових усуває різкий просторовий стрибок апертури:

1. **Прямокутне вікно (Uniform / Rectangular):** `w_m = 1.0`. Забезпечує гранично вузький головний промінь, проте рівень придушення першої бічної пелюстки становить лише `-13.3 дБ`. Це створює високу чутливість до бічних завад.
2. **Вікно Ганна (Hann):** `w_m = 0.5 - 0.5 · cos(2π m / (M-1))`. Знижує рівень бічних пелюсток до `-31.5 дБ` ціною розширення ширини головного променя за рівнем -3 дБ приблизно в 1.6 раза.
3. **Вікно Хеммінга (Hamming):** `w_m = 0.54 - 0.46 · cos(2π m / (M-1))`. Забезпечує оптимальне придушення найближчих бічних пелюсток до `-42.5 дБ`, що є стандартом для систем розпізнавання мови у зашумлених кімнатах.
4. **Вікно Блекмана (Blackman):** `w_m = 0.42 - 0.5 · cos(2π m / (M-1)) + 0.08 · cos(4π m / (M-1))`. Забезпечує глибоке придушення бічних завад до `-58.1 дБ` для прецизійної локалізації в умовах сильної луни.

## 5. Інваріанти структури даних та обробка виняткових станів

Під час ініціалізації та виконання обчислень програмний модуль повинен контролювати такі інваріанти:

### Валідація геометрії
- Кількість мікрофонів `num_mics` повинна належати інтервалу `[2, MAX_ARRAY_MICS]`. Масив з одного мікрофона не володіє просторовою вибірковістю.
- Мінімальна мікрофонна відстань `min_spacing` повинна перевищувати нуль (`min_spacing > 10⁻⁴ м`), щоб уникнути злиття координат сенсорів.
- Гранична частота просторового аліасингу `max_frequency_hz` автоматично розраховується як `c / (2 · min_spacing)`.

### Валідація кутів пеленгації
- Значення азимута `azimuth_deg` має бути нормалізоване до діапазону `[-180.0°, +180.0°]` або `[-90.0°, +90.0°]` для лінійних масивів.
- Кут місця `elevation_deg` повинен бути обмежений діапазоном `[-90.0°, +90.0°]`.

### Обробка несправностей сенсорів
У разі виходу з ладу окремого мікрофонного капсуля (постійний нуль, постійний шум або обрив лінії I2S/PDM) його ваговий коефіцієнт `w_m` примусово встановлюється в `0.0`, а ваги решти активних каналів перенормовуються для збереження одиничного сумарного підсилення.

## 6. Структури даних C та C++

Нижче наведено стандартизовані інтерфейсні структури даних для конфігурації геометрії та векторів рулювання.

:::tabs
```c
#ifndef ARRAY_GEOMETRY_SPEC_H
#define ARRAY_GEOMETRY_SPEC_H

#include <stddef.h>

#define MAX_ARRAY_MICS 32

typedef enum {
    TOPOLOGY_1D_LINEAR,
    TOPOLOGY_2D_CIRCULAR,
    TOPOLOGY_2D_PLANAR,
    TOPOLOGY_3D_SPHERICAL,
    TOPOLOGY_CUSTOM
} ArrayTopologyType;

typedef struct {
    float x; // координата X у метрах
    float y; // координата Y у метрах
    float z; // координата Z у метрах
} Vec3;

typedef struct {
    ArrayTopologyType type;
    size_t num_mics;
    Vec3 positions[MAX_ARRAY_MICS];
    float sound_speed;      // швидкість звуку c (м/с), за замовчуванням 343.0
    float sampling_rate;    // частота дискретизації fs (Гц)
    float min_spacing;      // мінімальна відстань між капсулями (м)
    float max_frequency_hz; // гранична частота f_alias без просторового аліасингу
} ArrayGeometryConfig;

typedef struct {
    float azimuth_deg;   // азимут [-180, +180] або [-90, +90]
    float elevation_deg; // кут місця [-90, +90]
    float delays_sec[MAX_ARRAY_MICS];
    float weights[MAX_ARRAY_MICS];
} SteeringVectorConfig;

// Ініціалізація 1D лінійного масиву
void init_linear_array(ArrayGeometryConfig* cfg, size_t num_mics, float spacing_m, float fs);

// Ініціалізація 2D кільцевого масиву
void init_circular_array(ArrayGeometryConfig* cfg, size_t num_mics, float radius_m, float fs);

// Розрахунок затримок та ваг для заданого кутового напрямку
void compute_steering_vector(const ArrayGeometryConfig* cfg, float azimuth_deg, float elevation_deg, SteeringVectorConfig* out);

#endif // ARRAY_GEOMETRY_SPEC_H
```
```cpp
#pragma once

#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <string_view>
#include <complex>

enum class ArrayTopology {
    Linear1D,
    Circular2D,
    Planar2D,
    Spherical3D,
    Custom
};

struct Point3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct SteeringVector {
    float azimuthDeg{0.0f};
    float elevationDeg{0.0f};
    std::vector<float> delaysSeconds;
    std::vector<float> weights;
    std::vector<std::complex<float>> phaseShifts;
};

class ArrayGeometry {
public:
    ArrayGeometry(ArrayTopology topology, std::vector<Point3D> micPositions,
                  float samplingRate = 16000.0f, float soundSpeed = 343.0f)
        : m_topology(topology), m_positions(std::move(micPositions)),
          m_fs(samplingRate), m_c(soundSpeed) {
        calculateAliasingLimit();
    }

    static ArrayGeometry createUniformLinear(std::size_t numMics, float spacingMeters, float fs = 16000.0f) {
        std::vector<Point3D> pos;
        pos.reserve(numMics);
        for (std::size_t i = 0; i < numMics; ++i) {
            pos.push_back({ static_cast<float>(i) * spacingMeters, 0.0f, 0.0f });
        }
        return ArrayGeometry(ArrayTopology::Linear1D, std::move(pos), fs);
    }

    static ArrayGeometry createUniformCircular(std::size_t numMics, float radiusMeters, float fs = 16000.0f) {
        std::vector<Point3D> pos;
        pos.reserve(numMics);
        for (std::size_t i = 0; i < numMics; ++i) {
            const float angle = 2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(numMics);
            pos.push_back({ radiusMeters * std::cos(angle), radiusMeters * std::sin(angle), 0.0f });
        }
        return ArrayGeometry(ArrayTopology::Circular2D, std::move(pos), fs);
    }

    [[nodiscard]] SteeringVector computeSteering(float azimuthDeg, float elevationDeg = 0.0f, float freqHz = 1000.0f) const {
        SteeringVector sv;
        sv.azimuthDeg = azimuthDeg;
        sv.elevationDeg = elevationDeg;
        sv.delaysSeconds.resize(m_positions.size());
        sv.weights.resize(m_positions.size(), 1.0f / static_cast<float>(m_positions.size()));
        sv.phaseShifts.resize(m_positions.size());

        const float azRad = azimuthDeg * std::numbers::pi_v<float> / 180.0f;
        const float elRad = elevationDeg * std::numbers::pi_v<float> / 180.0f;

        const Point3D u{
            std::sin(azRad) * std::cos(elRad),
            std::cos(azRad) * std::cos(elRad),
            std::sin(elRad)
        };

        for (std::size_t i = 0; i < m_positions.size(); ++i) {
            const float pathDiff = m_positions[i].x * u.x + m_positions[i].y * u.y + m_positions[i].z * u.z;
            sv.delaysSeconds[i] = pathDiff / m_c;
            const float phase = -2.0f * std::numbers::pi_v<float> * freqHz * sv.delaysSeconds[i];
            sv.phaseShifts[i] = std::complex<float>(std::cos(phase), std::sin(phase));
        }

        return sv;
    }

    [[nodiscard]] float getAliasingFrequencyHz() const noexcept { return m_aliasingFreqHz; }
    [[nodiscard]] std::size_t getNumMics() const noexcept { return m_positions.size(); }

private:
    void calculateAliasingLimit() {
        float minD = 1e6f;
        for (std::size_t i = 0; i < m_positions.size(); ++i) {
            for (std::size_t j = i + 1; j < m_positions.size(); ++j) {
                const float dx = m_positions[i].x - m_positions[j].x;
                const float dy = m_positions[i].y - m_positions[j].y;
                const float dz = m_positions[i].z - m_positions[j].z;
                const float d = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (d < minD && d > 1e-5f) minD = d;
            }
        }
        m_aliasingFreqHz = m_c / (2.0f * minD);
    }

    ArrayTopology m_topology;
    std::vector<Point3D> m_positions;
    float m_fs;
    float m_c;
    float m_aliasingFreqHz{0.0f};
};
```
:::
