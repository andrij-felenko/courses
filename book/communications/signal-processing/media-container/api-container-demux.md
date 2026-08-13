# 📋 Інтерфейс та контракт демультиплексора медіаконтейнера

Ця вставка є програмістською специфікацією C/C++ API та контракту демультиплексора медіаконтейнера (Demuxer) — фундаментального системного компонента медіаконвеєра, який зчитує потік байтів із джерела, розбирає ієрархічну структуру форматів (MP4, MKV, MPEG-TS, AVI) та розщеплює його на окремі елементарні пакети кадрів відео, аудіо чи субтитрів. У промислових медіадвигунах (таких як FFmpeg `libavformat`, GStreamer `qtdemux` / `matroskademux` або Android `MediaExtractor`) цей інтерфейс виконує роль абстрактного фасаду, що ізолює декодери від специфіки конкретного файлового формату.

Читач відкриває її для побудови неблокуючого демультиплексування з zero-copy буферизацією, обробки помилок та керування пам'яттю у високопродуктивних медіасистемах. Без чітко дотриманого API та контракту станів пристрої демультиплексування спричиняють витоки ресурсів, деградують за швидкодією через зайве копіювання байтових масивів у пам'яті або блокують основні потоки виконання під час затримок мережевого I/O чи зчитування з диска.

## 1. Архітектура автомата станів демультиплексора

Компонент демультиплексора працює за принципом скінченного автомата (Finite State Machine). Життєвий цикл модуля складається з шести послідовних станів:

1. **`STATE_UNINITIALIZED`:** Модуль створено, пам'ять контексту виділено, але файловий потік не відкритий.
2. **`STATE_OPENED`:** Проведено первинний відкриття файлу або сокета, вираховано базовий заголовок та підтверджено специфікацію контейнера.
3. **`STATE_HEADERS_PARSED`:** Прочитано індексні таблиці та глобальні метадані (`moov` у MP4 чи `Header/Tracks` у MKV). Сформовано списки треків та параметри кодеків.
4. **`STATE_STREAMING`:** Основний робочий стан. Модуль послідовно віддає пакети даних викликачу через метод `demuxer_read_packet()`.
5. **`STATE_SEEKING`:** Тимчасовий стан виклику операції переходу за часом. Модуль скидає внутрішні індексні вказівники та шукає найближчий опорний кадр.
6. **`STATE_END_OF_FILE`:** досягнуто кінець файлового потоку. Усі кадри видано, наступні виклики читання повертають код `EOF`.

## 2. Формальний опис структур даних

### 2.1. Перелічення типів медіапотоків та кодеків

Для уніфікованої ідентифікації доріжок у контейнері використовуються строго типізовані константи:

:::tabs
```c
typedef enum {
    MEDIA_TYPE_UNKNOWN = 0,
    MEDIA_TYPE_VIDEO,
    MEDIA_TYPE_AUDIO,
    MEDIA_TYPE_SUBTITLE
} MediaStreamType;

typedef enum {
    CODEC_ID_UNKNOWN = 0,
    CODEC_ID_H264,
    CODEC_ID_HEVC_H265,
    CODEC_ID_AV1,
    CODEC_ID_AAC,
    CODEC_ID_OPUS,
    CODEC_ID_PCM_S16LE
} MediaCodecID;
```
```cpp
enum class MediaStreamType : std::uint8_t {
    Unknown = 0,
    Video,
    Audio,
    Subtitle
};

enum class MediaCodecID : std::uint16_t {
    Unknown = 0,
    H264,
    HevcH265,
    Av1,
    Aac,
    Opus,
    PcmS16LE
};
```
:::

### 2.2. Метадані треку (`StreamInfo`)

Структура `StreamInfo` містить повний набір фізичних та програмних характеристик, необхідних для ініціалізації апаратних декодерів або графічних контекстів (OpenGL / Direct3D / Vulkan):

:::tabs
```c
typedef struct {
    uint32_t stream_index;        // Порядковий індекс треку в контейнері (0, 1, 2...)
    MediaStreamType type;          // Тип даних (відео, аудіо, субтитри)
    MediaCodecID codec_id;         // Ідентифікатор алгоритму стиснення
    uint32_t time_base_num;        // Чисельник часової шкали (наприклад, 1)
    uint32_t time_base_den;        // Знаменник часової шкали (наприклад, 90000 Гц)

    // Специфічні геометричні параметри відео
    uint32_t width;                // Ширина кадру в пікселях
    uint32_t height;               // Висота кадру в пікселях

    // Специфічні акустичні параметри аудіо
    uint32_t sample_rate;          // Частота дискретизації відліків (Гц)
    uint32_t channels;             // Кількість аудіоканалів (1 = моно, 2 = стерео, 6 = 5.1)

    // Спеціальний заголовок ініціалізації кодека (Codec Extradata)
    uint8_t *extradata;            // Вказівник на заголовок ініціалізації кодека
    size_t extradata_size;         // Розмір заголовка в байтах
} StreamInfo;
```
```cpp
struct StreamInfo {
    std::uint32_t stream_index{0};
    MediaStreamType type{MediaStreamType::Unknown};
    MediaCodecID codec_id{MediaCodecID::Unknown};
    std::uint32_t time_base_num{1};
    std::uint32_t time_base_den{90000};

    // Параметри відео
    std::uint32_t width{0};
    std::uint32_t height{0};

    // Параметри аудіо
    std::uint32_t sample_rate{0};
    std::uint32_t channels{0};

    // Заголовок ініціалізації кодека
    std::vector<std::uint8_t> extradata;
};
```
:::

### 2.3. Структура елементарного пакета (`MediaPacket`)

Одиниця зчитування стиснених даних з демультиплексора, яка передається безпосередньо у вхідний буфер декодера:

:::tabs
```c
typedef struct {
    uint32_t stream_index;        // Індекс треку, якому належить даний пакет
    uint8_t *data;                 // Буфер зі стисненим кадром (наприклад, NAL-одиниця)
    size_t size;                   // Розмір бувера у байтах
    int64_t pts;                   // Presentation Time Stamp (у тиках time_base)
    int64_t dts;                   // Decode Time Stamp (у тиках time_base)
    int64_t duration;              // Тривалість відтворення кадру у тиках
    uint32_t flags;                // Бітові прапорці стану пакета
} MediaPacket;

#define PACKET_FLAG_KEYFRAME (1 << 0)  // Пакет містить IDR / Ключовий кадр
#define PACKET_FLAG_CORRUPT  (1 << 1)  // Пакет містить виявлені завади каналу
```
```cpp
enum class PacketFlags : std::uint32_t {
    None     = 0,
    Keyframe = 1 << 0,
    Corrupt  = 1 << 1
};

struct MediaPacket {
    std::uint32_t stream_index{0};
    std::vector<std::uint8_t> data;
    std::int64_t pts{0};
    std::int64_t dts{0};
    std::int64_t duration{0};
    PacketFlags flags{PacketFlags::None};
};
```
:::

## 3. Сигнатури функцій API та контракт викликів

:::tabs
```c
// Відкриття джерела та первинний розбір заголовків контейнера
int demuxer_open(const char *url, void **context);

// Отримання кількості знайдених треків у медіаконтейнері
uint32_t demuxer_get_stream_count(void *context);

// Зчитування параметрів конкретного треку за його індексом
int demuxer_get_stream_info(void *context, uint32_t stream_index, StreamInfo *info);

// Послідовне зчитування наступного пакета кадрів з контейнера
int demuxer_read_packet(void *context, MediaPacket *packet);

// Звільнення пам'яті пакета після завершення обробки в декодері
void demuxer_free_packet(MediaPacket *packet);

// Точне або ключове позиціонування за часовим штампом (Seek)
int demuxer_seek(void *context, uint32_t stream_index, int64_t target_pts, int flags);

// Закриття контейнера та повне звільнення усіх системних ресурсів
void demuxer_close(void *context);
```
```cpp
class IDemuxer {
public:
    virtual ~IDemuxer() = default;

    virtual std::expected<void, std::string> open(std::string_view url) = 0;
    virtual std::uint32_t getStreamCount() const noexcept = 0;
    virtual std::expected<StreamInfo, std::string> getStreamInfo(std::uint32_t streamIndex) const = 0;
    virtual std::expected<MediaPacket, std::string> readPacket() = 0;
    virtual std::expected<void, std::string> seek(std::uint32_t streamIndex, std::int64_t targetPts, bool seekBackward) = 0;
};
```
:::

## 4. Суворі правила контракту та інваріанти поведінки

1. **Гарантія послідовності зчитування за DTS:** Метод `demuxer_read_packet()` повертає пакети строго у порядку зростання їхніх штампів декодування `DTS` у файлі. Це гарантує, що декодер отримує пакети у придатній для розпакування послідовності.
2. **Контракт володіння пам'яттю (Memory Ownership Contract):**
   - Буфер `packet->data` виділяється всередині модуля демультиплексора під час виконання `demuxer_read_packet()`.
   - Викликач (медіаплеєр або декодер) **зобов'язаний** викликати парну функцію `demuxer_free_packet()` після того, як пакет передано в апаратний прискорювач. У версії C++ вектор `std::vector<std::uint8_t>` утилізується автоматично завдяки RAII.
3. **Потокобезпечність (Thread Safety Model):** Виклики методів читання `demuxer_read_packet()` та позиціонування `demuxer_seek()` над одним і тим самим контекстом не є потокобезпечними. У мультипотокових плеєрах виклики демультиплексора мають захищатися внутрішнім м'ютексом (`std::mutex` або `pthread_mutex_t`).
4. **Контракт операції Seek (Seeking Invariants):**
   - При виклику `demuxer_seek()` демультиплексор скидає всі внутрішні прочитані буфери кадрів (Flush).
   - Якщо вказано прапорець `SEEK_FLAG_BACKWARD`, модуль зміщує покажчик на найближчий **попередній IDR-ключовий кадр**, чий `PTS <= target_pts`.
   - Перший пакет, який повертається методом `demuxer_read_packet()` одразу після успішного позиціонування, обов'язково містить встановлений бітовий прапорець `PACKET_FLAG_KEYFRAME`.

## 5. Управління буферним пулом та Zero-Copy передача даних

У високопродуктивних системах відеообробки (наприклад, при обробці відеопотоків 4K при 60-120 кадрах/с) виділення й звільнення пам'яті через класичні системні виклики `malloc()` та `free()` для кожного кадру створює неприпустимі накладні витрати й викликає фрагментацію оперативної пам'яті.

Для оптимізації роботи демультиплексор застосовує паттерн **буферного пулу (Buffer Pooling / Ring Buffer)**:

- При відкритті контейнера `demuxer_open()` модуль попередньо виділяє кільцевий буфер фіксованого розміру (наприклад, 16–32 Мбайт).
- Функція `demuxer_read_packet()` повертає вказівник на вже виділену ділянку всередині кільцевого буфера без виклику системного менеджера пам'яті.
- Виклик `demuxer_free_packet()` не звільняє пам'ять у систему, а лише повертає маркер покажчика в категорію доступних для повторного запису.

Для взаємодії з апаратними прискорювачами декодування (такими як NVDEC, VA-API чи V4L2 Statefull Decoders) демультиплексор може підтримувати **Zero-Copy режим**. У цьому режимі за допомогою файлових дескрипторів `DMA-BUF` або `mmap` стиснені кадри зчитуються з накопичувача безпосередньо у спеціалізовану пам'ять графічного процесора (VRAM) без проміжного копіювання в оперативну пам'ять CPU.

## 6. Асинхронні мережеві події та обробка помилок каналу

При роботі з мережевими потоками реального часу (RTSP, RTMP, WebRTC) демультиплексор стикається з мережевими затримками (Jitter), втратою IP-пакетів та динамічною зміною бітрейту.

Для обслуговування мережевих сокетів демультиплексор надає розширений асинхронний callback-інтерфейс:

:::tabs
```c
typedef void (*DemuxerPacketCallback)(MediaPacket *packet, void *user_data);
typedef void (*DemuxerErrorCallback)(int error_code, const char *msg, void *user_data);

int demuxer_set_callbacks(void *context, 
                          DemuxerPacketCallback pkt_cb, 
                          DemuxerErrorCallback err_cb, 
                          void *user_data);
```
```cpp
using PacketCallback = std::function<void(MediaPacket&& packet)>;
using ErrorCallback  = std::function<void(int errorCode, std::string_view message)>;

void setCallbacks(PacketCallback pktCb, ErrorCallback errCb);
```
:::

Якщо під час зчитування потоку мережевий сокет тимчасово блокується через відсутність даних, метод `demuxer_read_packet()` не повинен зависати нескінченно. Він повертає спеціальний код помилки `DEMUX_AGAIN` (-11), сигналізуючи медіаплеєру про необхідність виконати інші задачі або оновити інтерфейс користувача до появи нових пакетів у сокеті.
