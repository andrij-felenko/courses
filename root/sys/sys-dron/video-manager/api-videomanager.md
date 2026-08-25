# 📋 Контракт відеопідсистеми: властивості, виклики, сигнали й факти налаштувань

Тут зібрано все, що `VideoManager` віддає назовні — кожну властивість для QML із типом, правом запису й сигналом-сповіщенням, кожен викличний метод із передумовами, кожен сигнал, — а окремою таблицею всі факти групи `Video` з типами й типовими значеннями та позначкою, які з них узагалі не показують у збірці без GStreamer. Довідка потрібна, щоб підключити власний елемент інтерфейсу чи власну реалізацію приймача й наперед знати, яка прив'язка справді оновиться, а яка мовчки застигне на першому значенні.

Звірено з гілкою `master` репозиторію `mavlink/qgroundcontrol` 2 серпня 2026 року; чинна стабільна лінія на той час — 5.0.x. Файли: `src/VideoManager/VideoManager.{h,cc}`, `src/VideoManager/VideoReceiver/VideoReceiver.h`, `src/Settings/VideoSettings.{h,cc}`, `src/Settings/Video.SettingsGroup.json`, `src/FlyView/FlightDisplayViewVideo.qml`, `src/FlyView/FlightDisplayViewVideoOutput.qml`.

---

## Як дістатися до об'єкта

```cpp
class VideoManager : public QObject
{
    Q_OBJECT
    QML_ELEMENT
    QML_UNCREATABLE("")
```

Створити менеджер із QML не можна — тільки взяти готовий, і вхід до нього один: `QGroundControl.videoManager`. З C++ — `VideoManager::instance()`; об'єкт оголошений через `Q_APPLICATION_STATIC`, тобто народжується при першому звертанні й живе до кінця роботи застосунку.

Методи життєвого циклу з QML недоступні, і кличе їх лише сам застосунок:

```cpp
void init(QQuickWindow *mainWindow);   // після створення головного вікна
void startVideoBackendInit();          // довга ініціалізація бібліотеки конвеєра, у пулі
void cleanup();                        // повернути стоки плагінові ядра перед виходом
bool waitForVideoBackendReady(std::chrono::milliseconds timeout = std::chrono::minutes(1));
```

Останній потрібен лише тестам і будь-якому коду, якому відео знадобилося раніше, ніж бібліотека встигла піднятися: він блокує нитку, з якої його покликано, аж до готовності або до вичерпання хвилини.

---

## Властивості для QML

| Q_PROPERTY | Тип | Запис | NOTIFY | Звідки береться значення |
|---|---|---|---|---|
| `hasVideo` | `bool` | ні | `hasVideoChanged` | `streamEnabled && streamConfigured()` — обчислюється щоразу наново |
| `streaming` | `bool` | ні | `streamingChanged` | `streamingChanged` **основного** приймача |
| `decoding` | `bool` | ні | `decodingChanged` | `decodingChanged` основного приймача |
| `recording` | `bool` | ні | `recordingChanged(bool)` | `recordingChanged` основного приймача |
| `hasThermal` | `bool` | ні | ⚠ **`decodingChanged`** | у списку є тепловий приймач, чиї метадані потоку позначені як теплові |
| `isUvc` | `bool` | ні | `isUvcChanged` | ідентифікатор UVC непорожній **і** UVC доступний **і** `hasVideo()` |
| `isStreamSource` | `bool` | ні | `isStreamSourceChanged` | вибране джерело є в списку мережевих **або** спрацювало автоналаштування |
| `autoStreamConfigured` | `bool` | ні | `autoStreamConfiguredChanged` | метадані основного потоку є й їхній `uri()` непорожній |
| `fullScreen` | `bool` | **так**, `setfullScreen` | `fullScreenChanged` | просте поле менеджера; примусово скидається на `false` при втраті зв'язку й коли активного апарата не стало |
| `aspectRatio` | `double` | ні | `aspectRatioChanged` | три джерела за пріоритетом, див. нижче |
| `hfov` | `double` | ні | ⚠ `aspectRatioChanged` | `hfov()` метаданих основного потоку; інакше `1.0` |
| `thermalAspectRatio` | `double` | ні | ⚠ `aspectRatioChanged` | співвідношення сторін із метаданих теплового потоку; інакше `1.0` |
| `thermalHfov` | `double` | ні | ⚠ `aspectRatioChanged` | `hfov()` метаданих теплового потоку; інакше ⚠ **факт `aspectRatio`** |
| `videoSize` | `QSize` | ні | `videoSizeChanged` | розмір декодованого кадру основного приймача; до першого кадру порожній |
| `imageFile` | `QString` | ні | `imageFileChanged(QString)` | шлях, складений у `grabImage()` |
| `uvcVideoSourceID` | `QString` | ні | `uvcVideoSourceIDChanged` | ідентифікатор локальної камери, або порожній рядок |

Тепловий канал у цій таблиці підпорядкований усюди, крім трьох власних властивостей — `hasThermal`, `thermalAspectRatio` і `thermalHfov`. У кожного обробника сигналів приймача стоїть перевірка `!receiver->isThermal()`, тому `streaming`, `decoding`, `recording` й `videoSize` описують **лише** основний потік. Тепловий може йти й писатися, а `streaming` при цьому лишиться хибним.

Перша пастка — не в значеннях, а в сповіщеннях, і їх у таблиці позначено знаком ⚠. `hasThermal` оголошено з чужим сигналом:

```cpp
Q_PROPERTY(bool hasThermal READ hasThermal NOTIFY decodingChanged)
```

Отже, поява теплового потоку сама по собі прив'язку не оновить — оновить лише наступна зміна стану декодування основного каналу. Так само чотири дійсні властивості поділяють один сигнал `aspectRatioChanged`: кожна його поява перечитує всі чотири, і навпаки — зміна самого лише кута огляду без зміни розміру кадру нікого не розбудить.

Другу варто прочитати уважніше, бо вона єдина, де прив'язка застигне **назавжди**. `hasVideo()` читає два входи:

```cpp
bool VideoManager::hasVideo() const
{
    return (_videoSettings->streamEnabled()->rawValue().toBool() && _videoSettings->streamConfigured());
}
```

Жоден із них не з'єднано з `hasVideoChanged`: єдине місце, де цей сигнал вилітає, — перерахунок джерела, та й то тільки коли перерахунок справді щось змінив. Перемикання «Video Stream Enabled» до перерахунку не веде взагалі. Сам інтерфейс станції цю пастку обходить тим, що читає не властивість, а факт напряму:

```qml
text: QGroundControl.settingsManager.videoSettings.streamEnabled.rawValue
      ? qsTr("WAITING FOR VIDEO") : qsTr("VIDEO DISABLED")
```

Так само варто робити й у власному елементі: на прапорець «увімкнено» підписуються через [факт](root:sys-dron/fact-system), а `hasVideo` беруть як миттєвий знімок, а не як джерело оновлень.

Пріоритет джерел співвідношення сторін заданий явно й читається згори вниз:

```cpp
double VideoManager::aspectRatio() const
{
    // Живий розмір декодованого кадру важить найбільше
    if (!_videoSize.isEmpty()) {
        return static_cast<double>(_videoSize.width()) / _videoSize.height();
    }
    for (VideoReceiver *receiver : _videoReceivers) {          // далі — метадані камери
        QGCVideoStreamInfo *pInfo = receiver->videoStreamInfo();
        if (!receiver->isThermal() && pInfo && !pInfo->isThermal()) {
            return pInfo->aspectRatio();
        }
    }
    return _videoSettings->aspectRatio()->rawValue().toDouble();   // і аж потім налаштування
}
```

Практичний наслідок: факт `aspectRatio` з таблиці налаштувань діє **тільки доти, доки не пішли кадри**. Щойно приймач доповів розмір, значення з налаштувань перестає впливати на картинку, хоч і лишається в полі.

Ця сама сходинка в тепловому двійнику обірвана несиметрично. `hfov()` без метаданих повертає `1.0`, а `thermalHfov()` без метаданих повертає значення факта `aspectRatio` — тобто типово `1.777777` замість кута огляду. Число з таким походженням не означає нічого, і покладатися на `thermalHfov` можна лише тоді, коли `hasThermal` істинний.

---

## Викличні методи

Усі п'ять позначені `Q_INVOKABLE` і всі повертають `void` — про результат дізнаються тільки з властивостей і сигналів.

| Сигнатура | Що робить | Передумови | Чого НЕ робить |
|---|---|---|---|
| `void startVideo()` | перезапускає всі приймачі | `hasVideo()`; інакше — один рядок у журналі й вихід | не вмикає потік: якщо `streamEnabled` хибний, виклик безсилий |
| `void stopVideo()` | наказує зупинитися кожному приймачеві | — | ⚠ **не зупиняє надовго** (див. нижче) |
| `void startRecording(const QString &videoFile = QString())` | пише кожен приймач у свій файл | коректний `recordingFormat`, непорожній `videoSavePath`, і в приймача `started() == true` | не перекодовує; не зачіпає приймачів, які ще не запустилися |
| `void stopRecording()` | наказує спинити запис усім приймачам | — | не чекає на закриття файлу; про це скаже `recordingChanged(false)` |
| `void grabImage(const QString &imageFile = QString())` | складає шлях, публікує його й розсилає наказ | — | ⚠ сам кадру не зберігає (див. нижче) |

`stopVideo()` — найчастіше неправильно прочитаний виклик у всій підсистемі. Зупинка приймача проходить тим самим шляхом, що й перезапуск, а обробник завершення зупинки безумовно ставить нову спробу через секунду, якщо адреса не бита:

```cpp
receiver->setStarted(false);
if (status == VideoReceiver::STATUS_INVALID_URL) {
    qCDebug(VideoManagerLog) << "Invalid video URL. Not restarting";
} else {
    QTimer::singleShot(1000, receiver, [this, receiver]() { _startReceiver(receiver); });
}
```

Отже, «вимкнути відео» — це не `stopVideo()`, а `streamEnabled = false`. Виклик придатний лише там, де потік справді треба прибрати на короткий відомий проміжок; так ним і користуються — вікно відео при перекладанні з кутка на весь екран зупиняє потік і запускає таймер на дві секунди, щоб перезапуск стався вже після перебудови сцени.

Ім'я файлу запису складається з мітки часу з точністю до секунди, ім'я знімка — з мілісекундами, бо кадри йдуть частіше:

```
запис  →  <videoSavePath>/2026-08-02_14.31.07.mp4
         <videoSavePath>/2026-08-02_14.31.07.thermalVideo.mp4
знімок →  <photoSavePath>/2026-08-02_14.31.07.482.jpg
```

Обидві теки беруться не з групи `Video`, а з загальних налаштувань застосунку (`AppSettings::videoSavePath()` і `photoSavePath()`) — у самій групі `Video` запис `videoSavePath` є в метаданих, але доступу до нього VideoSettings не оголошує.

---

## Дві дороги знімка

`grabImage()` розсилає `takeScreenshot()` кожному приймачеві, а реалізація на GStreamer відповідає на цей наказ `STATUS_NOT_IMPLEMENTED`. Кадр насправді зберігає **інша сторона контракту** — сам елемент відео у QML, підписаний на властивісний сигнал:

```qml
Connections {
    target: QGroundControl.videoManager
    function onImageFileChanged(filename) {
        grabToImage(function(result) {
            if (!result.saveToFile(filename)) {
                console.error('Error capturing video frame');
            }
        });
    }
}
```

Це і є працездатний механізм знімка, і з нього випливають три речі. Знімок містить те, що намалював елемент, а не те, що прийшло з ефіру, — тобто вже після масштабування під розмір елемента. Сигнал несе повний шлях аргументом, тож власний елемент відео може підхопити його так само, нічого більше не реєструючи. І, оскільки той самий компонент використано двічі — для основного й для теплового каналу, — при ввімкненому тепловізорі на один виклик `grabImage()` припадає два незалежні збереження **за одним шляхом**: у файлі лишиться той кадр, чий зворотний виклик відпрацював останнім.

---

## Сигнали

| Сигнал | Аргументи | Коли |
|---|---|---|
| `hasVideoChanged` | — | перерахунок джерела щось змінив; **не** при зміні `streamEnabled` |
| `streamingChanged` | — | основний приймач почав або спинив прийом |
| `decodingChanged` | — | основний приймач почав або спинив декодування; ним же сповіщається `hasThermal` |
| `recordingChanged` | `bool recording` | основний приймач відкрив або закрив файл |
| `recordingStarted` | `const QString &filename` | ⚠ властивості не має: подія «файл справді відкрито», з неї стартує запис субтитрів |
| `videoSizeChanged` | — | основний приймач доповів новий розмір кадру |
| `aspectRatioChanged` | — | змінився розмір кадру **або** значення факта `aspectRatio` |
| `imageFileChanged` | `const QString &filename` | ⚠ не просто сповіщення: на ньому тримається знімок |
| `autoStreamConfiguredChanged` | — | автоналаштування від камери дало **нову** адресу |
| `isStreamSourceChanged` | — | разом із `hasVideoChanged`, з того самого перерахунку |
| `isUvcChanged` | — | змінився ідентифікатор локальної камери |
| `uvcVideoSourceIDChanged` | — | те саме, окремим сигналом |
| `fullScreenChanged` | — | запис у `fullScreen` або примусове скидання |
| `isAutoStreamChanged` | — | ⚠ жодна властивість не оголошує його своїм `NOTIFY` |

Останній рядок — не помилка читання заголовка: сигнал оголошено й він справді вилітає з перерахунку поруч із `hasVideoChanged` та `isStreamSourceChanged`, але властивості, яку він мав би сповіщати, у класі немає; ознака автоналаштування зветься `autoStreamConfigured` і має власний сигнал `autoStreamConfiguredChanged`. Підписуватися варто саме на другий.

Три сигнали з таблиці — `hasVideoChanged`, `isStreamSourceChanged`, `isAutoStreamChanged` — вилітають **тільки разом** і **тільки** тоді, коли перерахунок повернув «щось змінилося». Це наслідок порівняння нової адреси з тією, що вже стоїть у приймача: періодичні повідомлення камери про стан потоку не змінюють нічого й тому не породжують жодного сигналу.

---

## Факти групи `Video`

Група `Video` — двадцять один факт. Читаються вони з QML як `QGroundControl.settingsManager.videoSettings.<ім'я>`, з C++ — через `SettingsManager::instance()->videoSettings()`.

| Факт | Тип | Типове | Межі / перелік | Хто читає | Видно без GStreamer |
|---|---|---|---|---|---|
| `videoSource` | `string` | `Video Stream Disabled` | перелік будується під час запуску | менеджер | так |
| `udpUrl` | `string` | `0.0.0.0:5600` | — | менеджер | так |
| `rtspUrl` | `string` | *(порожньо)* | — | менеджер | так |
| `tcpUrl` | `string` | *(порожньо)* | — | менеджер | так |
| `streamEnabled` | `bool` | `true` | — | менеджер, інтерфейс | так |
| `aspectRatio` | `float` | `1.777777` | 6 знаків; `0.0` — не враховувати | менеджер (як запасне значення) | так |
| `videoFit` | `uint32` | `1` | `0` Fit Width · `1` Fit Height · `2` Fill · `3` No Crop | інтерфейс | так |
| `gridLines` | `bool` | `false` | — | інтерфейс | так |
| `showRecControl` | `bool` | `true` | — | інтерфейс | так |
| `recordingFormat` | `uint32` | `2` | `2` mp4 · `1` mov · `0` mkv | менеджер | так |
| `maxVideoSize` | `uint32` | `10240` МБ, на мобільних `2048` | не менше `100` | менеджер | так |
| `enableStorageLimit` | `bool` | `false`, на мобільних `true` | — | менеджер | так |
| `disableWhenDisarmed` | `bool` | `false` | — | ⚠ не менеджер | так |
| `rtspTimeout` | `uint32` | `8` с | не менше `1` | менеджер | **ні** |
| `lowLatencyMode` | `bool` | `false` | — | менеджер, перезапуск конвеєра | **ні** |
| `rtpJitterLatencyMs` | `uint32` | `80` мс | `0`…`2000` | менеджер, перезапуск конвеєра | **ні** |
| `rtspAutoReconnect` | `bool` | `true` | — | менеджер, **без** перезапуску | **ні** |
| `forceVideoDecoder` | `uint32` | `0` | `0` типово · `1` програмний · `8` апаратний · `2` NVIDIA · `3` VA-API · `4` DirectX3D 11 · `5` VideoToolbox · `6` Intel · `7` Vulkan | конвеєр; потрібен перезапуск застосунку | **ні** |
| `forceCpuVideoPath` | `bool` | `false` | — | конвеєр; потрібен перезапуск застосунку | **ні**, ще й лише на збірках із підтримкою пам'яті ГП |
| `videoConversionElement` | `string` | *(порожньо)* | ім'я елемента GStreamer | конвеєр | **ні** |
| `disablePixelAspectRatio` | `bool` | `false` | — | конвеєр | **ні** |

Стовпець «видно без GStreamer» вимагає точного прочитання, бо його легко зрозуміти навпаки. У збірці без GStreamer ці факти **не зникають**: вони існують, зберігаються, читаються кодом і доступні з QML — сховано лише їхній рядок у сторінці налаштувань:

```cpp
static constexpr bool kGstEnabled = false;      // коли QGC_GST_STREAMING не визначено
…
_rtspTimeoutFact->setUserVisible(kGstEnabled);
```

Тобто «невидимий» не означає «недієвий». Значення, колись збережене на збірці з GStreamer, житиме далі й впливатиме на поведінку, а користувач уже не зможе його побачити чи виправити. Для власного елемента налаштувань це означає: наявність факта перевіряти не треба, а от питати `userVisible` перед тим, як малювати рядок, — треба.

Три уточнення до окремих рядків.

**`maxVideoSize` без `enableStorageLimit` не робить нічого.** Прибирання старих записів починається з перевірки прапорця й на хибному значенні виходить одразу, ще не глянувши на диск. А типове значення прапорця на настільній платформі — `false`. Отже, стеля в 10240 МБ типово не діє взагалі; на мобільній, де прапорець типово ввімкнено, а стеля вп'ятеро нижча, — діє завжди.

**`recordingFormat` зберігає число, а не назву.** Перелік у налаштуваннях перерахований у порядку `mp4, mov, mkv` зі значеннями `2, 1, 0`, і ці числа — це індекси в переліку `FILE_FORMAT` приймача, якими прямо індексується таблиця розширень. Переставити пункти в інтерфейсі можна, перенумерувати — ні: чужі збережені налаштування після такої правки почнуть означати інший [контейнер](root:com-signal/media-container).

**`videoSource` зберігає англійський рядок-константу.** Метадані факта тримають дві паралельні послідовності — перекладені підписи для показу й початкові рядки для збереження, — і в файл налаштувань лягає саме другий:

```cpp
_nameToMetaDataMap[videoSourceName]->setEnumInfo(videoSourceCookedList, videoSourceList);
```

Тому порівнювати значення треба з константами (`VideoSettings::videoSourceRTSP` і рештою), а не з тим, що видно на екрані; з QML для цього є незмінні властивості `rtspVideoSource`, `udp264VideoSource`, `udp265VideoSource`, `tcpVideoSource`, `mpegtsVideoSource`, `disabledVideoSource`.

---

## Правила побудови адреси

Це найкорисніша частина контракту для того, хто ловить потік із чужого боку: показує, який саме рядок піде в приймач за кожного вибору джерела.

| Значення `videoSource` | Адреса, яку отримає приймач |
|---|---|
| `RTSP Video Stream` | `rtspUrl` як є |
| `UDP h.264 Video Stream` | `udp://<udpUrl>` |
| `UDP h.265 Video Stream` | `udp265://<udpUrl>` |
| `MPEG-TS Video Stream` | `mpegts://<udpUrl>` |
| `TCP-MPEG2 Video Stream` | `tcp://<tcpUrl>` |
| `3DR Solo (requires restart)` | `udp://0.0.0.0:5600` |
| `Parrot Discovery` | `udp://0.0.0.0:8888` |
| `Yuneec Mantis G` | `rtsp://192.168.42.1:554/live` |
| `Herelink AirUnit` | `rtsp://192.168.0.10:8554/H264Video` |
| `Herelink Hotspot` | `rtsp://192.168.43.1:8554/fpv_stream` |
| `Video Stream Disabled`, `No Video Available` | порожній рядок |
| ім'я USB-камери | порожній рядок — гілка йде повз приймач |

Схеми `udp265://` і `mpegts://` у стандартах не існують: це власна мова застосунку, якою вибір користувача доїжджає до приймача одним рядком. Вісім перших пунктів переліку додаються беззастережно; Herelink підставляється в одній із двох форм залежно від того, як зібрано застосунок, а імена USB-камер дописуються в кінець тим складом, який система бачить у мить запуску, — тож пункт зниклої камери зникає й із переліку, а збережений вибір скидається на «Video Stream Disabled».

Коли адресу диктує камера через [протокол камери MAVLink](root:sys-dron/mavlink-camera-gimbal), той самий рядок будується з поля `uri` повідомлення, і станція приймає обидві форми, які дозволяє стандарт, — і повну адресу, і самий лише номер порту:

| `VIDEO_STREAM_TYPE` | Значення `videoSource` | Адреса |
|---|---|---|
| `RTSP` | `RTSP Video Stream` | `uri` як є; додатково записується у факт `rtspUrl` |
| `TCP_MPEG` | `TCP-MPEG2 Video Stream` | `uri` як є |
| `RTPUDP`, кодування H.265 | `UDP h.265 Video Stream` | `uri`, або `udp265://0.0.0.0:<uri>`, якщо схеми в ньому нема |
| `RTPUDP`, решта | `UDP h.264 Video Stream` | `uri`, або `udp://0.0.0.0:<uri>` |
| `MPEG_TS` | `MPEG-TS Video Stream` | `uri`, або `mpegts://0.0.0.0:<uri>` |
| будь-який інший | `No Video Available` | `uri` як є, плюс попередження в журнал |

Результат цього перекладу записується назад у факти й [переживає перезапуск](root:sys-dron/settings-persistence), причому два записи розмежовані нерівно. Факт `videoSource` оновлює лише основний канал:

```cpp
if (settingsChanged) {
    if (!receiver->isThermal()) {
        _videoSettings->videoSource()->setRawValue(source);
    }
    emit autoStreamConfiguredChanged();
}
```

А от запис `rtspUrl` стоїть вище, просто в гілці `RTSP` перекладача, і перевірки на тепловий канал не має зовсім — тож теплова камера, яка віддає RTSP, перепише поле «RTSP URL» своєю адресою. Той, хто читає це поле, щоб дізнатися адресу картинки на екрані, отримає не її.

---

## Контракт із боку QML

Зв'язок «приймач ↔ елемент відео» тримається на іменах об'єктів, і це єдина його опора:

```cpp
static const QStringList videoStreamList = { "videoContent", "thermalVideo" };
…
QQuickItem *widget = window->findChild<QQuickItem*>(receiver->name());
if (!widget) {
    qCCritical(VideoManagerLog) << "stream widget not found" << receiver->name();
    _videoReceivers.removeOne(receiver);
    receiver->deleteLater();
    return;
}
```

Отже, дерево QML **зобов'язане** мати два об'єкти з такими іменами. Основному ім'я ставлять статично, тепловому — уже після завантаження, бо він створюється відкладено:

```qml
VideoOutput { objectName: "videoContent" }
```

```qml
Loader {
    sourceComponent: thermalOutputComponent
    onLoaded: { if (item) item.objectName = "thermalVideo" }
}
```

Рядок `thermalVideo` виконує ще одну роботу — саме за ним приймач визначає, що він тепловий:

```cpp
bool isThermal() const { return (_name == QStringLiteral("thermalVideo")); }
```

Тому перейменувати потік однією правкою неможливо: рядок доводиться міняти узгоджено і в C++, і в QML. А поламавши цей контракт, ви побачите не виняток і не порожній екран із поясненням, а один рядок у журналі й тихо знищений приймач.

---

## Перелічники приймача

Обидва оголошені в `VideoReceiver`, обидва позначені `Q_ENUM` і доступні з QML як `VideoReceiver.STATUS_OK` і подібні.

| `FILE_FORMAT` | Значення | Розширення |
|---|---|---|
| `FILE_FORMAT_MKV` | `0` (він же `FILE_FORMAT_MIN`) | `mkv` |
| `FILE_FORMAT_MOV` | `1` | `mov` |
| `FILE_FORMAT_MP4` | `2` (він же `FILE_FORMAT_MAX`) | `mp4` |

| `STATUS` | Значення | Що означає | Що робить менеджер на запуску |
|---|---|---|---|
| `STATUS_OK` | `0` | наказ виконано | позначає приймач запущеним і вмикає декодування |
| `STATUS_FAIL` | `1` | наказ провалився | нова спроба через 1000 мс |
| `STATUS_INVALID_STATE` | `2` | наказ недоречний: приймач уже це робить | нічого — чекає на зовнішню подію |
| `STATUS_INVALID_URL` | `3` | адреса непридатна | нічого; на зупинці — теж єдиний випадок без перезапуску |
| `STATUS_NOT_IMPLEMENTED` | `4` | наказ коректний, ця реалізація його не вміє | нічого |

Останнє значення — не заглушка від ліні, а частина контракту: реалізацій приймача кілька (GStreamer, полегшена, безекранна для тестів), і `STATUS_NOT_IMPLEMENTED` дозволяє їм чесно відповісти те, чого не скажуть ані «добре», ані «помилка». Пишучи власну реалізацію через [плагін ядра](root:sys-dron/core-plugin), відповідайте саме цим значенням на все, чого не підтримуєте, — тоді менеджер не піде в цикл спроб.

---

## Мінімальний робочий виклик

Панель, що показує стан підсистеми й керує записом, — усе, що потрібно для перевірки, чи контракт живий:

```qml
import QtQuick
import QtQuick.Controls
import QGroundControl

Column {
    property var _vm:       QGroundControl.videoManager
    property var _vs:       QGroundControl.settingsManager.videoSettings

    // Прив'язка на факт, а не на hasVideo: у hasVideo немає сигналу про цей вхід
    Text { text: _vs.streamEnabled.rawValue ? qsTr("Потік увімкнено") : qsTr("Потік вимкнено") }

    Text { text: qsTr("Прийом: ")   + (_vm.streaming ? "+" : "−") +
                 qsTr("  Декод: ")  + (_vm.decoding  ? "+" : "−") +
                 qsTr("  Тепловий: ") + (_vm.hasThermal ? "+" : "−") }

    Text {
        // videoSize порожній, доки не прийшов перший кадр
        text: _vm.videoSize.width > 0
              ? _vm.videoSize.width + "×" + _vm.videoSize.height
              : qsTr("кадрів ще не було")
    }

    Button {
        text:    _vm.recording ? qsTr("Спинити запис") : qsTr("Записувати")
        // запис іде лише з приймача, що вже запустився; USB-камера сюди не потрапляє
        enabled: _vm.streaming && !_vm.isUvc
        onClicked: _vm.recording ? _vm.stopRecording() : _vm.startRecording()
    }

    Button {
        text: qsTr("Знімок")
        onClicked: _vm.grabImage()   // шлях складе менеджер, збереже елемент відео
    }
}
```

З C++ найтиповіша задача — не керувати підсистемою, а дізнатися, куди насправді пішов потік, і зреагувати на початок запису:

```cpp
void MyTool::attach()
{
    VideoManager *vm = VideoManager::instance();
    VideoSettings *vs = SettingsManager::instance()->videoSettings();

    // Порівнюємо з константою, а не з тим, що показано користувачеві
    const QString source = vs->videoSource()->rawValue().toString();
    if (source == VideoSettings::videoSourceUDPH264) {
        qCDebug(MyLog) << "слухаємо" << QStringLiteral("udp://%1").arg(vs->udpUrl()->rawValue().toString());
    }

    // Ім'я файлу відоме лише тоді, коли приймач уже відкрив його
    connect(vm, &VideoManager::recordingStarted, this, [](const QString &filename) {
        qCDebug(MyLog) << "запис пішов у" << filename;
    });

    // Стеля сховища діє лише при ввімкненому прапорці — перевіряємо обидва факти
    if (vs->enableStorageLimit()->rawValue().toBool()) {
        qCDebug(MyLog) << "стеля" << vs->maxVideoSize()->rawValue().toUInt() << "МБ";
    }
}
```

---

## Пастки, помітні лише під час роботи

| Що зроблено | Що зламається | Чому мовчки |
|---|---|---|
| прив'язка до `hasVideo` як до джерела оновлень | застигне на першому значенні | обидва входи властивості не з'єднані з `hasVideoChanged` |
| прив'язка до `hasThermal` | оновиться із запізненням або ніколи | оголошено з чужим сигналом `decodingChanged` |
| `stopVideo()` як спосіб вимкнути відео | потік повернеться за секунду | обробник завершення зупинки безумовно ставить нову спробу |
| `startRecording()` при показі з USB-камери | файл не з'явиться, помилки не буде | локальна камера йде повз приймачі, у яких `started()` хибний |
| очікування, що `grabImage()` збереже кадр | файлу нема | приймач відповідає `STATUS_NOT_IMPLEMENTED`; зберігає елемент відео на сигнал `imageFileChanged` |
| знімок при ввімкненому тепловізорі | у файлі невідомо котрий із двох кадрів | обидва елементи відео підписані на один сигнал і пишуть за одним шляхом |
| порівняння `videoSource` з рядком з екрана | ніколи не збігається іншою мовою інтерфейсу | зберігається початкова англійська константа, показується переклад |
| надія на `maxVideoSize` без `enableStorageLimit` | диск заповниться до кінця | прибирання типово вимкнене на настільних платформах |
| перенумерування пунктів `recordingFormat` | чужі налаштування починають означати інший контейнер | зберігається число переліку, і воно ж індексує таблицю розширень |
| `thermalHfov` без перевірки `hasThermal` | замість кута огляду приходить `1.777777` | запасне значення взято з факта `aspectRatio` |
| факт `aspectRatio` як спосіб виправити картинку живого потоку | нічого не змінюється | живий розмір кадру має вищий пріоритет |
| читання `rtspUrl` як адреси показаного потоку | при тепловій RTSP-камері там чужа адреса | автоналаштування пише це поле з обох каналів, без перевірки на тепловий |
| підписка на `isAutoStreamChanged` | сигнал не сповіщає жодної властивості | ознака зветься `autoStreamConfigured` і має власний сигнал |
| елемент відео без `objectName` | приймач знищується при створенні | зв'язок тримається на `findChild` за іменем; слід — один рядок у журналі |
| збірка без GStreamer із чужим файлом налаштувань | ховані факти діють, але їх не видно | `setUserVisible(false)` ховає рядок, а не значення |
