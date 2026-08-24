# ⚙️ Ревізор збірки: програма, яка питає OpenCV, на що вона здатна

Це півтори сотні рядків на C++, які за частку секунди друкують усе, що конкретний бінарник OpenCV уміє в конкретній системі, — і з яких потім виймається кілька рядків для старту вашого застосунку, після чого «у замовника не працює, а в мене працює» перестає бути загадкою й стає повідомленням про помилку з назвою того, чого бракує.

## Задача

Опишемо неприємність точно — від точності залежить, що саме програма має вміти.

Служба обробки відео піднялася, під'єдналася до камери, сорок хвилин писала журнал без єдиної скарги. Потім оператор увімкнув запис — і `VideoWriter::isOpened()` повернув `false`. Жодного винятку, жодного рядка в журналі: невдале відкриття для `videoio` — не помилка, а звичайний результат, бо фасад просто перебрав доступні бекенди й жоден не взявся. Той самий образ контейнера на машині розробника пише файли справно.

Далі йде типовий вечір: зайти в контейнер, а там немає ані компілятора, ані вихідних текстів, ані мережі; зібрати пробну програму ніде; спробувати вгадати за назвою пакунка. Причина зрештою виявляється дрібною — не той плагін, не той кодек, не той шлях, — але коштує вона годин.

Отже, потрібна програма, яка задовольняє чотири вимоги, і кожна з них щось нам далі нав'язує:

- **вона нічого не потребує, крім самої OpenCV** — жодних вихідних текстів, жодного `pkg-config`, жодної мережі: усе, що вона друкує, вона бере з бібліотеки, яку вже завантажив процес;
- **вона не падає сама** — ревізор, що вилітає з винятком на третьому бекенді, гірший за відсутність ревізора, бо не дає навіть часткової картини;
- **вона вміє мовчати** — той самий код у режимі перевірки не друкує десять кілобайтів звіту, а дає одну відповідь: чого бракує і що з цим робити;
- **вона розрізняє «оголошено» і «працює»** — саме на цій різниці ламаються всі коротші спроби.

## Ідея: питань не одне, а чотири

Природний порив — написати «перевірити, чи є FFmpeg». Порив хибний, бо «є FFmpeg» — не одне твердження, а чотири різні, і в тій самій системі вони спокійно суперечать одне одному.

**Перше** живе в заголовках: макроси `CV_VERSION_MAJOR`, `CV_VERSION_MINOR`, `CV_VERSION_REVISION` і `HAVE_OPENCV_VIDEOIO` — це те, що бачив **ваш компілятор**. Ці числа зашиті у ваш об'єктний файл і про бібліотеку, яку підставить завантажувач, не знають нічого.

**Друге** — звіт конфігурації. `cv::getBuildInformation()` віддає той самий текст, що CMake надрукував наприкінці збірки: він потрапляє у згенерований файл `version_string.inc`, а звідти — у статичний рядок усередині `libopencv_core`. Це моментальний знімок **чужої машини в минулому**: що на ній знайшлося, коли бібліотеку складали. Незамінне свідчення про наміри — і жодного слова про те, що є тут і зараз.

**Третє** — реєстр `videoio`. `cv::videoio_registry::getStreamBackends()` перелічує бекенди, які **оголошено** в цій збірці й не вимкнено пріоритетом. Оголошено — не значить наявно: починаючи з 4.1 бекенд може бути не вкомпільований у `libopencv_videoio`, а лежати окремим файлом і завантажуватися під час виконання. Перелік складається з описів, а не з відкритих файлів; це звичайна властивість будь-якої [плагінної архітектури](topic:programming/plugin-architecture), де реєстр знає імена розширень раніше, ніж торкається їхнього коду.

**Четверте** — справжня спроба. `hasBackend()` уперше йде до файлової системи: для плагінного бекенда він викликає завантаження, і лише коли [динамічний завантажувач](topic:unix-linux/dynamic-loader) віддав дескриптор, а зашита в плагін версія ABI зійшлася з версією бібліотеки, відповідь стає `true`.

І навіть це не остання сходинка. Плагін, що завантажився, — це шлях до FFmpeg взагалі, а не до потрібного вам кодека всередині нього.

Якщо звузити питання до конкретного «чи прочитає ця збірка потік через FFmpeg», заголовки з переліку випадають — вони про версію, а не про здатність, — і сходинок знову виходить чотири, тільки інших.

![Чотири сходинки доказу: звіт конфігурації, реєстр бекендів, hasBackend і справжнє відкриття джерела; кожна доводить більше за попередню](img/evidence-ladder.svg)

*Кожна сходинка доводить більше за попередню — і жодна не доводить наступної.*

Звідси й будова програми: не «одна перевірка», а чотири окремі опитувачі, кожен зі своїм джерелом і своєю мірою певності, плюс один вузол, який зводить їх у вирок.

## Код

Усе далі — один файл `inspect_build.cpp`, поділений на частини лише для читання.

### Версія: два числа, що можуть розійтися

```cpp
#include <opencv2/core.hpp>
#include <opencv2/core/ocl.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/core/version.hpp>
#include <opencv2/core/utils/logger.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/videoio/registry.hpp>

#include <algorithm>
#include <cstdio>
#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace reg = cv::videoio_registry;

// CV_VERSION_* прийшли із заголовків, які бачив КОМПІЛЯТОР;
// getVersion*() виконується всередині тієї libopencv_core,
// яку підставив ЗАВАНТАЖУВАЧ. Це два незалежні числа.
static bool headerMatchesLibrary()
{
    return cv::getVersionMajor()    == CV_VERSION_MAJOR
        && cv::getVersionMinor()    == CV_VERSION_MINOR
        && cv::getVersionRevision() == CV_VERSION_REVISION;
}

static void reportVersion()
{
    std::cout << "OpenCV\n"
              << "  бібліотека: " << cv::getVersionString() << "\n"
              << "  заголовки:  " << CV_VERSION << "\n";
    if (!headerMatchesLibrary())
        std::cout << "  ! заголовки й бібліотека з різних збірок\n";
}
```

Перевірка виглядає зайвою рівно доти, доки не спрацює. Розходження означає, що в системі лежить кілька збірок, а зібрано вас проти одних заголовків, тоді як завантажувач знайшов інші, — і далі все залежить від того, чи розійшлася розкладка структур між цими двома версіями. Один рядок коштує п'яти хвилин, а ловить помилку, яка інакше проявиться аварією в геть іншому місці.

### Звіт конфігурації: розбирати, а не вивалювати

Спокуса — надрукувати `getBuildInformation()` цілком. Так роблять усі, і саме тому перевірку не вбудовують у застосунок: це десять кілобайтів тексту, у яких є все й не видно нічого. Але текст цей має правильну структуру, і за два рівні відступу з нього дістається будь-яке окреме значення:

```
  Video I/O:                       ← назва секції, рівно два пробіли
    FFMPEG:                    YES ← поле секції, чотири й більше
      avcodec:                 YES (60.31.102)
    GStreamer:                 YES (1.24.2)
```

Отже, читач має лише два правила: рядок із відступом два — початок секції, усе глибше до наступного такого рядка — її нутрощі.

```cpp
static std::string trimmed(const std::string& s)
{
    const size_t b = s.find_first_not_of(" \t\r");
    if (b == std::string::npos) return std::string();
    return s.substr(b, s.find_last_not_of(" \t\r") - b + 1);
}

static size_t indentOf(const std::string& s)
{
    const size_t b = s.find_first_not_of(' ');
    return b == std::string::npos ? 0 : b;
}

// Тіло секції звіту разом із її заголовком.
static std::vector<std::string> buildInfoSection(const std::string& name)
{
    static const std::vector<std::string> lines = [] {
        std::vector<std::string> v;
        std::istringstream in(cv::getBuildInformation());
        for (std::string ln; std::getline(in, ln); ) v.push_back(ln);
        return v;
    }();

    const std::string head = "  " + name + ":";
    std::vector<std::string> body;
    for (size_t i = 0; i < lines.size(); ++i) {
        if (lines[i].compare(0, head.size(), head) != 0) continue;
        body.push_back(lines[i]);
        for (size_t j = i + 1; j < lines.size(); ++j) {
            if (trimmed(lines[j]).empty()) continue;
            if (indentOf(lines[j]) <= 2) break;   // почалася наступна секція
            body.push_back(lines[j]);
        }
        break;
    }
    return body;
}

// buildInfoField("Video I/O", "FFMPEG") → "YES"
static std::string buildInfoField(const std::string& section,
                                  const std::string& key)
{
    const std::string tag = key + ":";
    for (const std::string& line : buildInfoSection(section)) {
        const size_t at = line.find(tag);
        if (at == std::string::npos || at != indentOf(line)) continue;
        return trimmed(line.substr(at + tag.size()));
    }
    return std::string();
}

// Значення в самому заголовку секції: «  Parallel framework:  pthreads»
static std::string buildInfoHead(const std::string& section)
{
    return buildInfoField(section, section);
}
```

Умова `at != indentOf(line)` тут не косметична: без неї `FFMPEG:` знайшлося б і в тілі чужого рядка, де слово стоїть усередині значення, а не на початку поля. Розбирач тексту, який приймає збіг будь-де, рано чи пізно збреше.

Тепер із десяти кілобайтів беруться потрібні півдесятка рядків — і саме їх не соромно покласти в журнал застосунку при старті.

### Реєстр: окремо оголошене, окремо завантажене

Це серце програми. Різницю між сходинками треба не описати в коментарі, а надрукувати в кожному рядку виведення.

```cpp
using PluginVersionFn = std::string (*)(cv::VideoCaptureAPIs, int&, int&);

// hasBackend() для плагіна — це справжня спроба завантажити файл.
static bool loads(cv::VideoCaptureAPIs api)
{
    try { return reg::hasBackend(api); }
    catch (const cv::Exception&) { return false; }
}

// Питати версію плагіна МОЖНА лише в плагіна: для вбудованого бекенда
// всередині спрацьовує CV_Assert і летить cv::Exception.
// Повертається опис із заголовка плагіна, а не шлях до файлу.
static std::string pluginNote(PluginVersionFn version, cv::VideoCaptureAPIs api)
{
    int abi = 0, apiVer = 0;
    try {
        const std::string desc = version(api, abi, apiVer);
        return " ← " + desc + " (ABI " + std::to_string(abi)
             + ", API " + std::to_string(apiVer) + ")";
    } catch (const cv::Exception&) {
        return " ← файл плагіна не відкрито";
    }
}

static void reportBackends(const char* what,
                           const std::vector<cv::VideoCaptureAPIs>& list,
                           PluginVersionFn version)
{
    std::cout << what << " (" << list.size() << ")\n";
    for (cv::VideoCaptureAPIs api : list) {
        const bool builtIn = reg::isBackendBuiltIn(api);
        const bool alive   = loads(api);
        std::cout << (alive ? "  + " : "  - ")
                  << reg::getBackendName(api)
                  << (builtIn ? "  вбудований" : "  плагін");
        if (!builtIn) std::cout << pluginNote(version, api);
        std::cout << "\n";
    }
}
```

Три однакові за формою виклики дають три різні відповіді, і це не надлишок:

```cpp
    reportBackends("Файли й потоки", reg::getStreamBackends(),
                                     reg::getStreamBackendPluginVersion);
    reportBackends("Камери",         reg::getCameraBackends(),
                                     reg::getCameraBackendPluginVersion);
    reportBackends("Запис",          reg::getWriterBackends(),
                                     reg::getWriterBackendPluginVersion);
```

Реєстр веде окремі списки, бо один бекенд не зобов'язаний уміти все: читати з файлу, відкривати камеру за номером і писати — це три різні здатності, і в описі кожного бекенда вони позначені незалежно. Є ще `getBackends()` — надмножина всього ввімкненого; він годиться для повноти картини, але для перевірки «чи зможу я записати» від нього користі рівно нуль. У свіжих 4.x з'явився ще й `getStreamBufferedBackends()` — у давніших збірках його немає, тому в переносній програмі його краще не чіпати.

### Обчислення: чим саме працюватиме бібліотека

```cpp
static void reportCompute()
{
    std::cout << "Паралелізм: " << buildInfoHead("Parallel framework")
              << ", потоків " << cv::getNumThreads()
              << " із " << cv::getNumberOfCPUs() << " процесорів\n";

    std::cout << "Вектори\n"
              << "  зібрано під: " << cv::getCPUFeaturesLine() << "\n"
              << "  процесор має:";
    for (int f : { CV_CPU_SSE4_2, CV_CPU_AVX, CV_CPU_AVX2,
                   CV_CPU_AVX512_SKX, CV_CPU_NEON })
        if (cv::checkHardwareSupport(f))
            std::cout << " " << cv::getHardwareFeatureName(f);
    std::cout << "\n";

    std::cout << "OpenCL: рантайм " << (cv::ocl::haveOpenCL() ? "є" : "немає")
              << ", T-API " << (cv::ocl::useOpenCL() ? "увімкнено" : "вимкнено")
              << "\n";
    if (!cv::ocl::haveOpenCL()) return;
    try {
        const cv::ocl::Device& dev = cv::ocl::Device::getDefault();
        if (!dev.empty())
            std::cout << "  " << dev.name() << " / " << dev.vendorName()
                      << " / " << dev.version()
                      << ", блоків " << dev.maxComputeUnits() << "\n";
    } catch (const cv::Exception& e) {
        std::cout << "  пристрій не піднявся: " << e.err << "\n";
    }
}
```

Два рядки про вектори стоять поряд навмисно, бо відповідають на різні питання. `getCPUFeaturesLine()` перелічує те, під що бібліотеку **скомпільовано**: базовий набір без позначки, диспетчеризовані — з зірочкою попереду, а знак питання в кінці означає «код є, але цей процесор його не потягне». `checkHardwareSupport()` натомість каже про **процесор**: чи має він таку інструкцію (і чи не заборонили її явно). Обидва потрібні: код без заліза марний так само, як залізо без коду. Звідки бібліотека взагалі дізнається про можливості процесора — окрема історія, [CPUID](topic:programming/cpuid).

Пара `haveOpenCL()` / `useOpenCL()` розрізняє так само чесно: перше — чи знайшовся рантайм у системі, друге — чи ввімкнений прозорий API просто зараз. Друге можна зняти зсередини процесу викликом `setUseOpenCL(false)` або ззовні змінною оточення, і тоді `cv::UMat` мовчки виконається на процесорі — картинка правильна, швидкість інша. Що саме перемикається під цим прапорцем — [бекенди й прискорення: UMat, OpenCL, апаратна збірка](topic:media-vision/opencv-backends).

## Від звіту до запобіжника

Звіт корисний людині. Застосункові потрібна не картина світу, а вирок: пускати чи ні. Тому та сама механіка збирається в другу форму — перелік обов'язкових здатностей, кожна з власним способом перевірки й власною порадою.

```cpp
struct Need {
    std::string           what;   // чого потребує застосунок
    std::function<bool()> probe;  // як це перевірити тут і тепер
    std::string           fix;    // що робити, якщо не склалося
};

static bool listed(const std::vector<cv::VideoCaptureAPIs>& list,
                   cv::VideoCaptureAPIs api)
{
    return std::find(list.begin(), list.end(), api) != list.end();
}

// Найтвердіший доказ: справді відкрити крихітний файл потрібним кодеком.
static bool writerWorks(int fourcc)
{
    const std::string probe = cv::tempfile(".mp4");
    cv::VideoWriter w(probe, cv::CAP_FFMPEG, fourcc, 25.0, cv::Size(64, 64));
    const bool ok = w.isOpened();
    w.release();
    std::remove(probe.c_str());
    return ok;
}
```

Перелік потрібного не вигадується в ревізорі — він виводиться з того, що застосунок і так знає про себе зі своєї [конфігурації](topic:programming/config-design): якщо джерело мережеве, потрібен бекенд для потоків; якщо ввімкнено запис, потрібен ще й записувач із конкретним кодеком.

```cpp
struct AppConfig {
    bool readsRtsp   = true;
    bool recordsH264 = true;
    bool usesOpenCL  = false;
};

static std::vector<Need> requirementsOf(const AppConfig& cfg)
{
    std::vector<Need> need;

    need.push_back({
        "заголовки й бібліотека OpenCV з однієї збірки",
        headerMatchesLibrary,
        "у процесі кілька збірок OpenCV; звірте, з чим злінковано плагіни" });

    if (cfg.readsRtsp)
        need.push_back({
            "читання RTSP через GStreamer",
            [] { return listed(reg::getStreamBackends(), cv::CAP_GSTREAMER)
                     && loads(cv::CAP_GSTREAMER); },
            "немає файлу opencv_videoio_gstreamer поруч із бібліотекою "
            "або в теках зі змінної OPENCV_VIDEOIO_PLUGIN_PATH" });

    if (cfg.recordsH264)
        need.push_back({
            "запис H.264 у mp4 через FFmpeg",
            [] { return listed(reg::getWriterBackends(), cv::CAP_FFMPEG)
                     && writerWorks(cv::VideoWriter::fourcc('a','v','c','1')); },
            "бекенд запису є, але кодек avc1 у ньому не піднімається — "
            "перевірте, з якою збіркою FFmpeg зібрано плагін" });

    if (cfg.usesOpenCL)
        need.push_back({
            "OpenCL для cv::UMat",
            [] { return cv::ocl::haveOpenCL() && cv::ocl::useOpenCL(); },
            "рантайму OpenCL немає або його вимкнено; "
            "конвеєр на UMat тихо порахується на процесорі" });

    return need;
}

static bool verify(const std::vector<Need>& needs)
{
    std::vector<const Need*> missing;
    for (const Need& n : needs) {
        bool ok = false;
        try { ok = n.probe(); }
        catch (const cv::Exception&) { ok = false; }
        if (!ok) missing.push_back(&n);
    }
    if (missing.empty()) return true;

    std::cerr << "Ця збірка OpenCV (" << cv::getVersionString()
              << ") не дає застосункові потрібного:\n";
    for (const Need* n : missing)
        std::cerr << "  x " << n->what << "\n      " << n->fix << "\n";
    std::cerr << "Повний перелік здатностей: запустіть із --report.\n";
    return false;
}
```

`try` навколо кожної проби — не перестрахування, а вимога з початку: перевірка, яка сама впала, перетворює зрозумілу відмову на незрозумілу аварію, тобто робить рівно те, проти чого затіяна.

І останнє — `main`, у якому обидві форми співіснують:

```cpp
int main(int argc, char** argv)
{
    const std::string mode = argc > 1 ? argv[1] : "--report";

    if (mode == "--debug")   // чому саме плагін не завантажився
        cv::utils::logging::setLogLevel(cv::utils::logging::LOG_LEVEL_DEBUG);

    if (mode != "--check") {
        reportVersion();
        std::cout << "Модулі: "
                  << buildInfoField("OpenCV modules", "To be built") << "\n"
                  << "Contrib: "
                  << buildInfoField("Extra modules", "Version control (extra)")
                  << "\n";
        reportBackends("Файли й потоки", reg::getStreamBackends(),
                                         reg::getStreamBackendPluginVersion);
        reportBackends("Камери",         reg::getCameraBackends(),
                                         reg::getCameraBackendPluginVersion);
        reportBackends("Запис",          reg::getWriterBackends(),
                                         reg::getWriterBackendPluginVersion);
        reportCompute();
        std::cout << "\n";
    }

    const AppConfig cfg{};               // насправді — з конфігурації застосунку
    return verify(requirementsOf(cfg)) ? 0 : 1;
}
```

Збирається це звичайним `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.16)
project(inspect_build CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED COMPONENTS core videoio)
add_executable(inspect_build inspect_build.cpp)
target_link_libraries(inspect_build PRIVATE ${OpenCV_LIBS})
```

`${OpenCV_LIBS}` замість переліку цілей на кшталт `opencv_core opencv_videoio` — свідомо: у збірці з `opencv_world` окремих бібліотек просто немає, тож і цілей із такими іменами CMake не знайде. Змінна натомість правильна в обох випадках.

Типове виведення в контейнері, де плагіни поставили не туди:

```
OpenCV
  бібліотека: 4.13.0
  заголовки:  4.13.0
Модулі: core dnn features2d flann imgcodecs imgproc video videoio
Contrib:
Файли й потоки (3)
  + FFMPEG  плагін ← FFmpeg OpenCV Video I/O plugin (ABI 1, API 1)
  - GSTREAMER  плагін ← файл плагіна не відкрито
  + CV_IMAGES  вбудований
Запис (2)
  + FFMPEG  плагін ← FFmpeg OpenCV Video I/O plugin (ABI 1, API 1)
  - GSTREAMER  плагін ← файл плагіна не відкрито

Ця збірка OpenCV (4.13.0) не дає застосункові потрібного:
  x читання RTSP через GStreamer
      немає файлу opencv_videoio_gstreamer поруч із бібліотекою
      або в теках зі змінної OPENCV_VIDEOIO_PLUGIN_PATH
```

Від мовчазного `isOpened() == false` через сорок хвилин це відрізняється не зручністю, а породою відмови: тут названо причину в момент її виникнення, там — наслідок через півдня. Загальне правило, з якого це випливає, — [жодна помилка не мовчить](topic:programming/error-handling); у службі ту саму функцію природно вішають ще й на [перевірку готовності](topic:programming/health-checks), щоб оркестратор не пускав на екземпляр трафік, якого той не потягне.

## Пастки

**«Бекенд у реєстрі» — не «плагін завантажився».** Найдорожча помилка з усіх, і саме її роблять усі короткі перевірки. `getStreamBackends()` повертає описи з таблиці, складеної під час збірки: імена, пріоритети, ролі. Файлової системи ці функції не торкаються взагалі. Перевірку, що чогось варта, робить тільки `hasBackend()`. Тому в переліку обов'язкового завжди стоять обидві умови поспіль: є в потрібному списку — і завантажується.

**`hasBackend()` має побічну дію.** Він не «дивиться», а завантажує: тягне в процес `libavcodec` з усім гроном, а разом із ним — глобальний стан і конструктори бібліотеки. Перебирати ним усі бекенди підряд у ревізорі правильно (на те він і ревізор), а в старті служби — ні: перевіряйте рівно ті, що записані як обов'язкові. Пробні виклики зазвичай кешуються, тож повторне звертання вже нічого не завантажує, але перше коштує реального `dlopen`.

**Плагін шукається не там, де ви думаєте.** Файл із бекендом шукається в теці самої бібліотеки OpenCV і в теках зі змінної `OPENCV_VIDEOIO_PLUGIN_PATH`, за шаблоном імені: до `opencv_videoio_` додається ім'я бекенда малими літерами, далі будь-який суфікс і розширення платформи — тобто під шаблон однаково підходять `libopencv_videoio_ffmpeg.so` і `opencv_videoio_ffmpeg4130_64.dll`. Конкретний файл можна нав'язати змінною виду `OPENCV_VIDEOIO_PLUGIN_FFMPEG`, а на Windows у FFmpeg є ще й власна `OPENCV_FFMPEG_DLL_DIR`. Практичний висновок для контейнера: пакувальник, який кладе бібліотеки в одну теку, а плагіни — в іншу, ламає збірку, не змінивши в ній жодного байта.

**Ревізор не покаже, який саме файл завантажився.** Запит версії плагіна повертає опис із його заголовка — рядок на кшталт `FFmpeg OpenCV Video I/O plugin` — і дві версії: мінімальну підтримувану й фактичну версію API. Шляху там немає взагалі. Коли `hasBackend()` каже «ні», а файл начебто на місці, або коли підозрюєте, що завантажився не той файл, відповідь дає лише журнал: `OPENCV_VIDEOIO_DEBUG=1` чи `setLogLevel(LOG_LEVEL_DEBUG)` покажуть, у яких теках бібліотека шукала, що знайшла й на чому спіткнулася.

**Питати версію плагіна у вбудованого бекенда — виняток.** `getStreamBackendPluginVersion()` усередині зводить фабрику бекенда до плагінної через `dynamic_cast` і перевіряє результат через `CV_Assert`. Для вбудованого бекенда зведення не вдається, і летить `cv::Exception`; для плагіна, що не завантажився, — те саме, тільки з іншого місця. Звідси порядок у коді: спершу `isBackendBuiltIn()`, і лише потім, під `try`, питання про версію.

**Читання й запис — різні набори.** Те, що бекенд є в списку читання, не каже про список запису нічого: це окремі поля в описі бекенда, і збіг між списками — властивість конкретної збірки, а не правило. Перевірка «зможу писати», зроблена за списком джерел, показує «так» рівно доти, доки писати не доведеться по-справжньому.

**Навіть записувач, який відкрився, не доводить, що кодек є.** Бекенд запису — це шлях до бібліотеки; кодек `avc1` усередині неї може бути не зібраний або відрізаний ліцензійно. Єдиний повний доказ — відкрити справжній записувач 64×64 у тимчасовий файл: це кілька мілісекунд і один файл, який ви одразу прибираєте. Та сама логіка діє й на боці читання, тільки там вона дорожча: справжня перевірка джерела означає з'єднання з камерою, тож у старті служби зазвичай спиняються на `hasBackend()`, а перше відкриття лишають першому кадру — але з чесним повідомленням, а не мовчанням.

**Збірка з `opencv_world` плутає картину.** У ній усі модулі склеєні в одну бібліотеку, тож рядок `To be built` у звіті перелічує їх усі, як і раніше, — а окремих файлів `libopencv_videoio.so` на диску немає. Ознака в звіті одна: `world` присутній серед побудованого, а не в переліку вимкнених. Наслідок практичний: перелік цілей у `target_link_libraries` треба брати зі змінної `${OpenCV_LIBS}`, а спроба поставити поряд «звичайну» збірку й `world`-збірку дає два повні набори символів OpenCV в одному процесі — ситуацію, у якій жодна перевірка вже не рятує.

**Пусті рядки у звіті — норма.** `Contrib:` у виведенні вище порожній не через помилку розбирача, а тому, що секції `Extra modules` у звіті немає взагалі: цю збірку зроблено без другого репозиторію. Розбирач мусить повертати порожній рядок і для «поля немає», і для «поле є, значення порожнє» — розрізняти ці випадки нема потреби, а от падати, коли секції немає, він не має права.

**Ціна.** Повний звіт — це один `dlopen` на кожен плагінний бекенд плюс розбір десяти кілобайтів тексту, разом одиниці або десятки мілісекунд, залежно від того, скільки важать бібліотеки, що підтягнуться слідом. Перевірка на старті з трьох-чотирьох потреб коштує менше, якщо не чіпати зайвих бекендів, і рівно один справжній `VideoWriter` — якщо ви таки хочете знати про кодек напевно. Це та ціна, яку варто платити щоразу, коли застосунок запускається не на вашій машині.
