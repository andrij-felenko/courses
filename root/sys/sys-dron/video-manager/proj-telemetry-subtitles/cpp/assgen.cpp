// збірка: g++ -std=c++17 -O2 -Wall assgen.cpp -o assgen
// запуск: ./assgen 1280 720 30 > flight.ass
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <string>
#include <vector>

// ─── ЩО ПОКАЗУЄМО ─────────────────────────────────────────────────────────

struct Reading {
    std::string name;    // «Висота»
    std::string value;   // «12.4 м»
};

// Джерело показів: «дай стан на t-й секунді від початку запису».
// У станції сюди підставляють поточні значення панелі телеметрії.
using Sampler = std::function<std::vector<Reading>(double)>;

// ─── РОЗКЛАДКА ────────────────────────────────────────────────────────────

struct Layout {
    int width   = 1280;
    int height  = 720;
    int columns = 3;     // скільки пар «назва: значення» по горизонталі
    int spread  = 100;   // наскільки розсунути крайні колонки до країв
    int gap     = 10;    // просвіт між назвою і значенням
    int bottom  = 30;    // відступ низу блока від низу кадру
};

static int fontSize(const Layout &L)
{
    const int fs = (L.width * 12) / 640;   // 12 при 640 → та сама частка кадру
    return (fs < 8) ? 8 : fs;
}

// x, до якого притискається лівий край значень i-ї колонки (i від нуля)
static int columnX(const Layout &L, int i)
{
    const int stride = (L.width + L.spread) / (L.columns + 1);
    return -(L.spread / 2) + stride * (i + 1);
}

// ─── ЧАС У ВИГЛЯДІ, ЯКИЙ ВИМАГАЄ ASS: H:MM:SS.cc ──────────────────────────

static std::string timecode(double seconds)
{
    long cs = (seconds > 0.0) ? std::lround(seconds * 100.0) : 0;
    const long h = cs / 360000; cs %= 360000;
    const long m = cs / 6000;   cs %= 6000;
    const long s = cs / 100;    cs %= 100;

    char buf[32];
    std::snprintf(buf, sizeof(buf), "%ld:%02ld:%02ld.%02ld", h, m, s, cs);
    return std::string(buf);
}

// ─── ЗНЕЗБРОЄННЯ ТЕКСТУ ───────────────────────────────────────────────────
// Стандарт ASS не має екранування взагалі: «{» відкриває блок команд,
// «\» починає команду, перенос рядка обриває подію. Вміст тут наш власний,
// тож найчесніше — просто не пускати ці знаки у файл.
// Перевірка побайтова, і для UTF-8 це безпечно: жоден із цих кодів
// не трапляється всередині багатобайтової літери.

static std::string sanitize(const std::string &in)
{
    std::string out;
    out.reserve(in.size());
    for (const char c : in) {
        switch (c) {
        case '{':  out += '('; break;
        case '}':  out += ')'; break;
        case '\\': out += '/'; break;
        case '\n':
        case '\r': out += ' '; break;
        default:   out += c;   break;
        }
    }
    return out;
}

// ─── ЗАГОЛОВОК СЦЕНАРІЮ ───────────────────────────────────────────────────

static std::string header(const Layout &L)
{
    return
        "[Script Info]\n"
        "Title: Telemetry overlay\n"
        "ScriptType: v4.00+\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        "PlayResX: " + std::to_string(L.width) + "\n"
        "PlayResY: " + std::to_string(L.height) + "\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Monospace," + std::to_string(fontSize(L)) + ","
        "&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
        "0,0,0,0,100,100,0,0,1,2,2,1,10,10,10,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n";
}

// ─── ОДНА ПОДІЯ ───────────────────────────────────────────────────────────

static std::string dialogue(double t0, double t1, int x, int y,
                            const char *align, const std::string &text)
{
    return "Dialogue: 0," + timecode(t0) + "," + timecode(t1) +
           ",Default,,0,0,0,,{" + align +
           "\\pos(" + std::to_string(x) + "," + std::to_string(y) + ")}" +
           text + "\n";
}

// ─── ПИСЬМЕННИК ───────────────────────────────────────────────────────────

static void writeSubtitles(std::FILE *out, const Layout &L,
                           const Sampler &sample, double duration, double rate)
{
    std::fputs(header(L).c_str(), out);

    const double step = 1.0 / rate;
    const int y = L.height - L.bottom;

    for (long k = 0; (k * step) < duration; ++k) {
        const double t0 = k * step;          // від номера, а не накопиченням
        const double t1 = (k + 1) * step;

        const std::vector<Reading> r = sample(t0);   // знімок на ПОЧАТКУ інтервалу
        if (r.empty()) {
            continue;
        }

        const int n = static_cast<int>(r.size());
        const int per = (n + L.columns - 1) / L.columns;   // стеля ділення

        for (int c = 0; c < L.columns; ++c) {
            std::string names;
            std::string values;
            for (int j = c * per; (j < (c + 1) * per) && (j < n); ++j) {
                if (!names.empty()) {
                    names  += "\\N";
                    values += "\\N";
                }
                names  += sanitize(r[j].name) + ":";
                values += sanitize(r[j].value);
            }
            if (names.empty()) {
                continue;
            }

            const int x = columnX(L, c);
            std::fputs(dialogue(t0, t1, x - L.gap, y, "\\an3", names).c_str(), out);
            std::fputs(dialogue(t0, t1, x,         y, "\\an1", values).c_str(), out);
        }
    }
}

// ─── ДЕМОНСТРАЦІЙНЕ ДЖЕРЕЛО ───────────────────────────────────────────────

static std::string fmt(const char *spec, double v)
{
    char buf[64];
    std::snprintf(buf, sizeof(buf), spec, v);
    return std::string(buf);
}

static std::vector<Reading> demoFlight(double t)
{
    return {
        { "Висота",    fmt("%.1f м",   40.0 * (1.0 - std::exp(-t / 12.0))) },
        { "Швидкість", fmt("%.1f м/с", 8.0 + 3.0 * std::sin(t / 5.0)) },
        { "Курс",      fmt("%.0f°",    std::fmod(t * 9.0, 360.0)) },
        { "Батарея",   fmt("%.2f В",   16.8 - 0.004 * t) },
        { "Політ",     fmt("%.0f с",   t) },
        { "Супутники", "12" },
        { "Режим",     "AUTO" },
    };
}

int main(int argc, char **argv)
{
    Layout L;
    double duration = 30.0;
    double rate = 1.0;

    if (argc > 2) {
        L.width  = std::atoi(argv[1]);
        L.height = std::atoi(argv[2]);
    }
    if (argc > 3) { duration = std::atof(argv[3]); }
    if (argc > 4) { rate     = std::atof(argv[4]); }

    writeSubtitles(stdout, L, demoFlight, duration, rate);
    return 0;
}
