// gpx2geojson.cpp — потоковий перетворювач GPX-треків на GeoJSON.
//   c++ -O2 -std=c++17 -Wall -o gpx2geojson gpx2geojson.cpp -lexpat
//   ./gpx2geojson track.gpx > track.geojson
// Потрібен to_chars/from_chars для double: libstdc++ 11+, MSVC 19.24+.

#include <expat.h>
#include <cctype>
#include <charconv>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <type_traits>

namespace {

constexpr int IOBUF   = 64 * 1024;
constexpr int NAMEMAX = 512;

enum Cap { CAP_NONE, CAP_ELE, CAP_TIME, CAP_GEOID, CAP_NAME };
enum Ele { ELE_AUTO, ELE_ELLIPSOID, ELE_NONE };

struct Pt {
    double lat = 0, lon = 0;
    bool   has_pos = false;
    std::optional<double> ele, geoid;
    std::optional<std::string> time;
};

[[noreturn]] void die(const char *msg) {
    std::fprintf(stderr, "gpx2geojson: %s\n", msg);
    std::exit(1);
}

// to_chars НЕ дивиться на локаль — крапка гарантована самим стандартом
std::string fixed(double v, int digits) {
    char buf[64];
    auto r = std::to_chars(buf, buf + sizeof buf, v, std::chars_format::fixed, digits);
    if (r.ec != std::errc{}) die("число не форматується");
    return std::string(buf, r.ptr);
}

std::optional<double> parse_num(std::string_view s) {
    auto sp = [](char c) { return std::isspace(static_cast<unsigned char>(c)) != 0; };
    while (!s.empty() && sp(s.front())) s.remove_prefix(1);
    while (!s.empty() && sp(s.back()))  s.remove_suffix(1);
    double v = 0;
    auto r = std::from_chars(s.data(), s.data() + s.size(), v);
    if (r.ec != std::errc{} || r.ptr != s.data() + s.size()) return std::nullopt;
    return v;
}

std::string json_quote(std::string_view s) {
    std::string o = "\"";
    for (unsigned char c : s) {
        switch (c) {
        case '"':  o += "\\\""; break;
        case '\\': o += "\\\\"; break;
        case '\n': o += "\\n";  break;
        case '\r': o += "\\r";  break;
        case '\t': o += "\\t";  break;
        default:
            if (c < 0x20) { char u[8]; std::snprintf(u, sizeof u, "\\u%04x", c); o += u; }
            else o += static_cast<char>(c);
        }
    }
    return o + '"';
}

std::string_view trimmed(std::string_view s) {
    auto sp = [](char c) { return std::isspace(static_cast<unsigned char>(c)) != 0; };
    while (!s.empty() && sp(s.front())) s.remove_prefix(1);
    while (!s.empty() && sp(s.back()))  s.remove_suffix(1);
    return s;
}

// <gpx:trkpt> і <trkpt> для нас те саме
std::string_view local(const XML_Char *n) {
    std::string_view v{n};
    auto p = v.rfind(':');
    return p == std::string_view::npos ? v : v.substr(p + 1);
}

struct Conv {
    XML_Parser xp = nullptr;
    std::FILE *out = stdout;
    int  digits = 7, ele_mode = ELE_AUTO;
    bool want_times = true;

    int depth = 0, d_ext = 0, d_trk = 0, d_seg = 0, d_pt = 0;

    Cap cap = CAP_NONE;
    std::string text, name;

    Pt   cur, pend;
    bool pend_valid = false;

    long feats = 0;  bool feat_open = false;
    long segs  = 0;  bool seg_open  = false;  long in_seg = 0;

    bool   dim_fixed = false, dim3 = false;
    double last_ele = 0, last_geoid = 0;

    long pts = 0, no_time = 0, ele_carried = 0, geoid_carried = 0,
         segs_dropped = 0, pts_bad = 0, trks_empty = 0;

    std::string times;                 // готовий текст масиву часів треку
    const char *abort_why = nullptr;

    void put(std::string_view s) { std::fwrite(s.data(), 1, s.size(), out); }

    void emit_pos(const Pt &p) {
        if (!dim_fixed) {              // вимір визначає перша виведена точка
            dim3 = ele_mode == ELE_AUTO      ? (p.ele && p.geoid)
                 : ele_mode == ELE_ELLIPSOID ? bool(p.ele) : false;
            dim_fixed = true;
        }
        std::string s = "[" + fixed(p.lon, digits) + "," + fixed(p.lat, digits);
        if (dim3) {
            if (p.ele) last_ele = *p.ele; else ++ele_carried;
            double h = last_ele;
            if (ele_mode == ELE_AUTO) {          // h = H + N
                if (p.geoid) last_geoid = *p.geoid; else ++geoid_carried;
                h += last_geoid;
            }
            s += "," + fixed(h, 2);
        }
        put(s + "]");
    }

    void emit_time(const Pt &p) {
        if (!p.time) ++no_time;
        if (!want_times) return;
        times += p.time ? json_quote(*p.time) : "null";   // дірка, не пропуск
    }

    void emit_point(const Pt &p) {
        if (!feat_open) {
            if (feats) put(",\n");
            put(R"({"type":"Feature","geometry":)"
                R"({"type":"MultiLineString","coordinates":[)");
            feat_open = true;
        }
        if (!seg_open) {
            if (segs) { put(","); if (want_times) times += ','; }
            put("[");             if (want_times) times += '[';
            seg_open = true; in_seg = 0;
        }
        if (in_seg) { put(","); if (want_times) times += ','; }
        emit_pos(p);
        emit_time(p);
        ++in_seg; ++pts;
    }

    void pt_begin(const XML_Char **atts) {
        cur = Pt{};
        std::optional<double> lat, lon;
        for (int i = 0; atts[i]; i += 2) {
            auto a = local(atts[i]);
            if      (a == "lat") lat = parse_num(atts[i + 1]);
            else if (a == "lon") lon = parse_num(atts[i + 1]);
        }
        if (lat && lon && *lat >= -90 && *lat <= 90 && *lon >= -180 && *lon <= 180) {
            cur.lat = *lat; cur.lon = *lon; cur.has_pos = true;
        }
    }

    void pt_end() {
        if (!cur.has_pos) { ++pts_bad; return; }
        if (pend_valid) emit_point(pend);      // попередня вже не одинока
        pend = cur; pend_valid = true;
    }

    void seg_end() {
        if (pend_valid && seg_open) emit_point(pend);
        pend_valid = false;
        if (seg_open) {
            put("]"); if (want_times) times += ']';
            ++segs; seg_open = false;
        } else {
            ++segs_dropped;   // нуль або одна точка — лінії з такого не буває
        }
    }

    void trk_begin() {
        feat_open = seg_open = pend_valid = false;
        segs = in_seg = 0;
        name.clear();
        dim_fixed = dim3 = false; last_ele = last_geoid = 0;
        pts = no_time = ele_carried = geoid_carried = segs_dropped = pts_bad = 0;
        times.clear();            // довжина в нуль, місткість лишається
    }

    void trk_end() {
        if (!feat_open) { ++trks_empty; return; }
        put(R"(]},"properties":{"name":)");
        put(name.empty() ? "null" : json_quote(name));

        const char *ed = !dim3 ? "none"
                       : ele_mode == ELE_AUTO ? "wgs84-ellipsoid (ele + geoidheight)"
                                              : "wgs84-ellipsoid (ele прийнято за h)";
        char tail[512];
        std::snprintf(tail, sizeof tail,
            ",\"elevation\":\"%s\",\"conversion\":{\"digits\":%d,\"points\":%ld,"
            "\"segments\":%ld,\"segments_dropped\":%ld,\"points_without_time\":%ld,"
            "\"elevation_carried\":%ld,\"geoidheight_carried\":%ld,"
            "\"points_dropped\":%ld}",
            ed, digits, pts, segs, segs_dropped, no_time,
            ele_carried, geoid_carried, pts_bad);
        put(tail);

        if (want_times) {
            put(R"(,"coordinateProperties":{"times":[)");
            put(times);
            put("]}");
        }
        put("}}");
        ++feats;
    }
};

void XMLCALL on_start(void *ud, const XML_Char *el, const XML_Char **atts) {
    auto *c = static_cast<Conv *>(ud);
    auto n = local(el);
    ++c->depth;

    if (c->d_ext) return;                        // усередині extensions — сліпі
    if (n == "extensions") { c->d_ext = c->depth; return; }

    if (!c->d_trk) {
        if (n == "trk") { c->d_trk = c->depth; c->trk_begin(); }
        return;
    }
    if (!c->d_seg) {
        if (n == "trkseg") { c->d_seg = c->depth; c->seg_open = false; }
        else if (n == "name" && c->name.empty()) { c->cap = CAP_NAME; c->text.clear(); }
        return;
    }
    if (!c->d_pt) {
        if (n == "trkpt") { c->d_pt = c->depth; c->pt_begin(atts); }
        return;
    }
    if      (n == "ele")         { c->cap = CAP_ELE;   c->text.clear(); }
    else if (n == "time")        { c->cap = CAP_TIME;  c->text.clear(); }
    else if (n == "geoidheight") { c->cap = CAP_GEOID; c->text.clear(); }
}

// текст одного вузла приходить ЧАСТИНАМИ — дописуємо, не перезаписуємо
void XMLCALL on_text(void *ud, const XML_Char *t, int len) {
    auto *c = static_cast<Conv *>(ud);
    if (c->cap == CAP_NONE) return;
    if (c->text.size() < 64 * 1024) c->text.append(t, static_cast<size_t>(len));
}

void XMLCALL on_end(void *ud, const XML_Char *el) {
    auto *c = static_cast<Conv *>(ud);
    int d = c->depth--;
    (void)el;

    if (c->d_ext) { if (d == c->d_ext) c->d_ext = 0; return; }

    if (c->cap != CAP_NONE) {
        auto v = trimmed(c->text);
        switch (c->cap) {
        case CAP_ELE:   c->cur.ele   = parse_num(v); break;
        case CAP_GEOID: c->cur.geoid = parse_num(v); break;
        case CAP_TIME:  if (!v.empty()) c->cur.time = std::string(v); break;
        case CAP_NAME:  c->name.assign(v.substr(0, NAMEMAX)); break;
        default: break;
        }
        c->cap = CAP_NONE;
        return;
    }
    if (d == c->d_pt)  { c->d_pt  = 0; c->pt_end();  return; }
    if (d == c->d_seg) { c->d_seg = 0; c->seg_end(); return; }
    if (d == c->d_trk) { c->d_trk = 0; c->trk_end(); return; }
}

// у GPX сутностей не буває — оголошення сутності означає чужий намір
void XMLCALL on_entity(void *ud, const XML_Char *, int, const XML_Char *, int,
                       const XML_Char *, const XML_Char *,
                       const XML_Char *, const XML_Char *) {
    auto *c = static_cast<Conv *>(ud);
    c->abort_why = "у вхідному файлі оголошено сутність (DOCTYPE) — відхилено";
    XML_StopParser(c->xp, XML_FALSE);
}

}  // namespace

int main(int argc, char **argv) {
    Conv c;
    const char *path = nullptr;

    for (int i = 1; i < argc; i++) {
        std::string_view a{argv[i]};
        if (a == "-d" && i + 1 < argc) {
            c.digits = std::atoi(argv[++i]);
            if (c.digits < 0 || c.digits > 9) die("-d поза межами 0..9");
        } else if (a == "--ele" && i + 1 < argc) {
            std::string_view m{argv[++i]};
            if      (m == "auto")      c.ele_mode = ELE_AUTO;
            else if (m == "ellipsoid") c.ele_mode = ELE_ELLIPSOID;
            else if (m == "none")      c.ele_mode = ELE_NONE;
            else die("--ele: auto | ellipsoid | none");
        } else if (a == "--no-times") {
            c.want_times = false;
        } else {
            path = argv[i];
        }
    }

    std::FILE *in = path ? std::fopen(path, "rb") : stdin;
    if (!in) die("не відкривається вхідний файл");

    auto parser = std::unique_ptr<std::remove_pointer_t<XML_Parser>,
                                  decltype(&XML_ParserFree)>(
        XML_ParserCreate(nullptr), &XML_ParserFree);   // кодування — з декларації
    if (!parser) die("не створюється парсер");
    c.xp = parser.get();
    XML_SetUserData(c.xp, &c);
    XML_SetElementHandler(c.xp, on_start, on_end);
    XML_SetCharacterDataHandler(c.xp, on_text);
    XML_SetEntityDeclHandler(c.xp, on_entity);

    c.put("{\"type\":\"FeatureCollection\",\"features\":[\n");

    for (;;) {
        void *buf = XML_GetBuffer(c.xp, IOBUF);
        if (!buf) die("бракує пам'яті у парсері");
        std::size_t got = std::fread(buf, 1, IOBUF, in);
        if (std::ferror(in)) die("помилка читання входу");
        int last = (got == 0);
        if (XML_ParseBuffer(c.xp, static_cast<int>(got), last) == XML_STATUS_ERROR) {
            std::fprintf(stderr, "gpx2geojson: %s (рядок %lu: %s)\n",
                         c.abort_why ? c.abort_why : "розбір XML не вдався",
                         static_cast<unsigned long>(XML_GetCurrentLineNumber(c.xp)),
                         XML_ErrorString(XML_GetErrorCode(c.xp)));
            return 2;                        // вивід недописаний і невалідний
        }
        if (last) break;
    }

    c.put("\n]}\n");
    if (path) std::fclose(in);
    std::fprintf(stderr, "gpx2geojson: треків виведено %ld, порожніх пропущено %ld\n",
                 c.feats, c.trks_empty);
    if (std::fflush(c.out) || std::ferror(c.out)) die("вивід записався не повністю");
    return 0;
}
