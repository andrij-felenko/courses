// збірка: g++ -std=c++17 -Wall -Wextra source_resolution.cpp -o srcres && ./srcres
#include <cstdio>
#include <optional>
#include <string>

// ─── ВХОДИ ────────────────────────────────────────────────────────────────

// У застосунку джерело — рядок у факті налаштувань («UDP h.264 Video Stream»
// і подібні). Тут перелік: логіка від написання рядків не залежить.
enum class Source { NoVideo, UdpH264, UdpH265, MpegTs, Rtsp, Tcp };

struct Settings {
    Source      source        = Source::NoVideo;
    std::string udpUrl        = "0.0.0.0:5600";  // мережева частина для UDP і MPEG-TS
    std::string rtspUrl;
    std::string tcpUrl;
    bool        streamEnabled = true;            // «показувати відео» взагалі
    bool        lowLatency    = false;           // режим низької затримки
    int         rtpJitterMs   = 200;             // глибина буфера вирівнювання
    bool        autoReconnect = true;            // перепід'єднуватися після невдачі
};

// Те, що приїхало в VIDEO_STREAM_INFORMATION від камери на борту.
enum class StreamType { Rtsp, RtpUdp, TcpMpeg, MpegTs };
enum class Encoding   { Unknown, H264, H265 };

struct StreamInfo {
    StreamType  type     = StreamType::RtpUdp;
    Encoding    encoding = Encoding::H264;
    std::string uri;      // повна адреса АБО самий номер порту — дозволено обидва
};

// Те, що зараз стоїть у приймача. Не прихований стан, а такий самий вхід.
struct ReceiverState {
    std::optional<std::string> uri;      // порожній optional = ще нічого не призначали
    bool lowLatency    = false;
    int  rtpJitterMs   = 0;
    bool autoReconnect = false;
};

// ─── ВИХІД ────────────────────────────────────────────────────────────────

struct Decision {
    std::string uri;                        // що має стояти в приймача
    bool        lowLatency    = false;
    int         rtpJitterMs   = 0;
    bool        autoReconnect = false;
    bool        hasVideo      = false;      // увімкнено І налаштовано
    bool        changed       = false;      // щось із того, що йде в конвеєр, стало іншим
    std::optional<Source> writeBackSource;  // джерело, продиктоване апаратом
};

enum class Action { Nothing, Restart, Stop };

// ─── ДОПОМІЖНЕ ────────────────────────────────────────────────────────────

static bool isAllDigits(const std::string &s)
{
    if (s.empty()) return false;
    for (char c : s) {
        if (c < '0' || c > '9') return false;
    }
    return true;
}

// «5600» → «udp://0.0.0.0:5600»; повну адресу лишаємо як є.
static std::string withScheme(const std::string &scheme, const std::string &raw)
{
    if (raw.find("://") != std::string::npos) return raw;
    if (isAllDigits(raw))  return scheme + "://0.0.0.0:" + raw;  // самий порт
    return scheme + "://" + raw;                                 // «хост:порт» без схеми
}

// Чи справді нова адреса інша. Порожній optional означає «ще не призначали»,
// і це НЕ те саме, що призначена порожня адреса.
static bool uriDiffers(const ReceiverState &rx, const std::string &uri)
{
    return !(rx.uri.has_value() && *rx.uri == uri);
}

// Чи є взагалі що вмикати: у кожного типу джерела своє поле адреси.
static bool configured(const Settings &st, const std::optional<StreamInfo> &info)
{
    if (info.has_value()) return true;         // апарат сказав сам — налаштовано
    switch (st.source) {
    case Source::UdpH264:
    case Source::UdpH265:
    case Source::MpegTs:  return !st.udpUrl.empty();
    case Source::Rtsp:    return !st.rtspUrl.empty();
    case Source::Tcp:     return !st.tcpUrl.empty();
    case Source::NoVideo: return false;
    }
    return false;
}

// ─── РІШЕННЯ: чиста функція ───────────────────────────────────────────────

static Decision resolve(const Settings &st,
                        const std::optional<StreamInfo> &info,
                        const ReceiverState &rx)
{
    Decision d;
    d.lowLatency    = st.lowLatency;
    d.rtpJitterMs   = st.rtpJitterMs;
    d.autoReconnect = st.autoReconnect;

    if (info.has_value()) {
        // Апарат диктує: тип потоку з протоколу стає джерелом застосунку.
        switch (info->type) {
        case StreamType::Rtsp:
            d.writeBackSource = Source::Rtsp;
            d.uri = info->uri;                         // RTSP приходить повною адресою
            break;
        case StreamType::RtpUdp:
            if (info->encoding == Encoding::H265) {
                d.writeBackSource = Source::UdpH265;
                d.uri = withScheme("udp265", info->uri);
            } else {
                d.writeBackSource = Source::UdpH264;
                d.uri = withScheme("udp", info->uri);
            }
            break;
        case StreamType::MpegTs:
            d.writeBackSource = Source::MpegTs;
            d.uri = withScheme("mpegts", info->uri);
            break;
        case StreamType::TcpMpeg:
            d.writeBackSource = Source::Tcp;
            d.uri = withScheme("tcp", info->uri);
            break;
        }
    } else {
        // Ручний вибір: тип вирішує, яку схему приклеїти до поля адреси.
        switch (st.source) {
        case Source::UdpH264: d.uri = "udp://"    + st.udpUrl;  break;
        case Source::UdpH265: d.uri = "udp265://" + st.udpUrl;  break;
        case Source::MpegTs:  d.uri = "mpegts://" + st.udpUrl;  break;
        case Source::Rtsp:    d.uri = st.rtspUrl;               break;
        case Source::Tcp:     d.uri = "tcp://"    + st.tcpUrl;  break;
        case Source::NoVideo: d.uri.clear();                    break;
        }
    }

    d.hasVideo = st.streamEnabled && configured(st, info);

    // Накопичення прапорця. КОЖЕН крок мусить відпрацювати — звідси |=, не ||.
    d.changed |= uriDiffers(rx, d.uri);
    d.changed |= (st.lowLatency  != rx.lowLatency);
    d.changed |= (st.rtpJitterMs != rx.rtpJitterMs);
    // autoReconnect свідомо НЕ тут: його читають на ходу.

    return d;
}

// ─── ДІЯ: усе, що псує стан, зібрано в одному місці ───────────────────────

static Action apply(const Decision &d, ReceiverState &rx, Settings &st)
{
    rx.autoReconnect = d.autoReconnect;          // жива величина — щоразу, без наслідків

    if (d.writeBackSource.has_value()) {
        st.source = *d.writeBackSource;          // вибір апарата стає вибором у налаштуваннях
    }
    if (!d.changed) {
        return Action::Nothing;                  // конвеєр не чіпаємо
    }

    rx.uri         = d.uri;
    rx.lowLatency  = d.lowLatency;
    rx.rtpJitterMs = d.rtpJitterMs;
    return d.hasVideo ? Action::Restart : Action::Stop;
}
