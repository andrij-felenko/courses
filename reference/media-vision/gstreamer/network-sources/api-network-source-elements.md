# 📋 Контракт мережевих елементів GStreamer: властивості, caps і транспорт

Ця довідка збирає в одному місці все, чим налаштовують приймання відео з мережі: властивості `udpsrc`, `rtspsrc`, `rtpjitterbuffer` і депейлоадерів, поля caps `application/x-rtp`, правило переведення SDP у ці поля та рядки транспорту RTSP. Дані взято з чинної гілки GStreamer 1.x (`gst-plugins-good`); там, де властивість з'явилася пізніше за 1.0, стоїть позначка випуску. Остаточну відповідь для вашої збірки завжди дає `gst-inspect-1.0 <елемент>` — версії відрізняються не назвами, а значеннями за замовчуванням.

## Одиниці: перше, на чому спотикаються

Сусідні властивості сусідніх елементів міряють час у різних одиницях, і жодна назва про це не попереджає.

| Властивість | Одиниця | Приклад «дві секунди» |
|---|---|---|
| `udpsrc timeout` | наносекунди | `timeout=2000000000` |
| `rtspsrc timeout`, `rtspsrc tcp-timeout` | **мікросекунди** | `timeout=2000000` |
| `rtspsrc teardown-timeout` | наносекунди | `teardown-timeout=2000000000` |
| `rtspsrc latency`, `rtpjitterbuffer latency` | мілісекунди | `latency=2000` |
| `rtpjitterbuffer rtx-*`, `max-misorder-time`, `max-dropout-time` | мілісекунди | `rtx-delay=2000` |
| `udpsrc buffer-size`, `rtspsrc udp-buffer-size` | байти | — |

> 🔧 **Навіщо це.** `rtspsrc timeout=5000` виглядає як «п'ять секунд» і читається як «п'ять секунд», а означає п'ять мілісекунд: елемент здасться на UDP майже миттєво й піде в TCP на кожному лінку, навіть цілком здоровому. Симптом — картинка є, затримка велика, `protocols=udp` не працює ніколи. Перевірка одна: поділіть своє число на мільйон і спитайте, чи це схоже на секунди.

## udpsrc: сокет як джерело

| Властивість | Тип | Типово | Що робить |
|---|---|---|---|
| `port` | int | 5004 | порт, на якому слухає; `0` — хай систему вибере сама |
| `address` | string | `0.0.0.0` | адреса для `bind`; групова адреса вмикає приєднання до групи |
| `caps` | GstCaps | NULL | що саме лежить у датаграмах — оголошення, а не перевірка |
| `buffer-size` | int | 0 | `SO_RCVBUF` приймального сокета в байтах; `0` — як налаштована система |
| `mtu` | uint | 1492 | розмір буферів у пулі, з якого беруть пам'ять під датаграму |
| `auto-multicast` | bool | true | приєднатися до групи на `PLAYING` і вийти з неї на зупинці |
| `multicast-iface` | string | NULL | інтерфейс, з якого слати запит на приєднання |
| `multicast-source` | string | NULL | список джерел для фільтрації за джерелом (IGMPv3) |
| `loop` | bool | true | чи повертати на цю ж машину те, що вона сама шле в групу |
| `reuse` | bool | true | `SO_REUSEADDR` перед `bind` |
| `timeout` | uint64 | 0 | після скількох наносекунд тиші слати повідомлення; `0` — не слати |
| `skip-first-bytes` | int | 0 | скільки байтів відрізати з початку кожної датаграми |
| `socket` | GSocket | NULL | готовий сокет ззовні замість власного |
| `close-socket` | bool | true | чи закривати переданий ззовні сокет на зупинці |
| `used-socket` | GSocket | — | лише читання: сокет, який працює зараз |
| `retrieve-sender-address` | bool | true | чіпляти до кожного буфера адресу відправника (`GstNetAddressMeta`) |
| `uri` | string | `udp://0.0.0.0:5004` | той самий порт і адреса одним рядком |

Чотири з цих властивостей поводяться не так, як підказує назва.

**`caps` — це присяга, а не фільтр.** `udpsrc` не заглядає всередину датаграми; він просто чіпляє до вихідного паду те, що ви написали. Помилилися в `payload` чи `clock-rate` — жодної помилки не буде, буде тиша, бо депейлоадер шукатиме в пакетах не те, що в них лежить. Без `caps` пад лишається без опису формату, і [узгодження з наступним елементом](book:media-vision/caps-negotiation) просто нема на чому побудувати — з'єднання не постане.

**`buffer-size` — це прямо `SO_RCVBUF`.** Якщо система не дозволяє такий розмір, елемент не падає, а пише в журнал попередження «Could not create a buffer of requested … bytes. Need net.admin privilege?» і працює далі з тим, що дали. Ядро Linux, до того ж, обмежує запит стелею `net.core.rmem_max` і подвоює прийняте значення для власного обліку — тож прочитане назад число не дорівнює записаному. [Опції сокета](book:programming/socket-options) — окрема тема; тут важливо лише, що це не внутрішня черга GStreamer, а буфер ядра, і переповнюється він мовчки.

**`mtu` — це розмір комірки в пулі пам'яті, а не межа пакета.** Датаграма, більша за `mtu`, не обрізається: елемент домалює до буфера ще один шматок пам'яті. Ціна помилки тут не в утрачених даних, а у зайвій алокації на кожен великий пакет — помітно на високих бітрейтах, невидимо на низьких.

**`timeout` нічого не зупиняє.** Він лише кладе на шину елементне повідомлення зі структурою `GstUDPSrcTimeout`; конвеєр далі чекає так само. Рішення — перепідключитися, звалитися з помилкою, показати «немає сигналу» — цілком за вашим кодом.

```c
/* udpsrc timeout=2000000000  →  повідомлення на шину після 2 с тиші */
static gboolean
on_bus (GstBus * bus, GstMessage * msg, gpointer user_data)
{
  const GstStructure *s = gst_message_get_structure (msg);

  if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ELEMENT &&
      s && gst_structure_has_name (s, "GstUDPSrcTimeout")) {
    guint64 ns = 0;
    gst_structure_get_uint64 (s, "timeout", &ns);
    g_printerr ("тиша в сокеті довша за %" G_GUINT64_FORMAT " нс\n", ns);
  }
  return TRUE;                  /* повідомлення не «спожите» — хай іде далі */
}
```

Групове приймання має рівно одну пастку, і вона не в GStreamer. Запит на приєднання до групи ядро шле з якогось інтерфейсу, і на машині з кількома мережами воно вибере той, куди дивиться маршрут за замовчуванням, — а потік іде іншим. `multicast-iface=eth1` каже, з якого саме; `multicast-source` звужує приймання до перелічених відправників, як дозволяє [фільтрація за джерелом](book:communications/source-specific-multicast). Механіка самого приєднання розібрана в темі про [багатоадресну розсилку](book:programming/multicast-and-discovery).

Найдешевша перевірка «чи взагалі щось прилітає» обходиться без кодеків узагалі:

```sh
gst-launch-1.0 -v udpsrc port=5600 ! fakesink dump=true
```

Порожній вивід означає, що до конвеєра не дійшло нічого, і далі шукати треба у фаєрволі чи в маршруті, а не в налаштуваннях елементів.

## rtspsrc: сеанс і все, що з нього випливає

`rtspsrc` — не елемент, а зібраний на ходу підконвеєр із власним менеджером сеансу. Тому половина його властивостей нічого не робить сама, а лише передає значення всередину.

| Властивість | Тип | Типово | Що робить |
|---|---|---|---|
| `location` | string | NULL | `rtsp://…` або `rtsps://…`; логін і пароль можна вписати сюди ж |
| `latency` | uint | **2000** мс | вікно очікування внутрішнього буфера джитера |
| `protocols` | flags | `udp+udp-mcast+tcp` | які нижні транспорти дозволено пробувати |
| `buffer-mode` | enum | `auto` | режим внутрішнього буфера джитера |
| `do-rtcp` | bool | true | слати звіти приймача й приймати звіти відправника |
| `do-retransmission` | bool | **true** | просити повтори втрачених пакетів (RFC 4588) |
| `drop-on-latency` | bool | false | викидати найстаріше замість рости понад `latency` |
| `ntp-sync` | bool | false | вести вихідні мітки часу за абсолютним часом зі звітів RTCP |
| `ntp-time-source` | enum | `ntp` | що вважати абсолютним часом: `ntp`, `unix`, `running-time`, `clock-time` |
| `timeout` | uint64 | 5000000 мкс = **5 с** | скільки чекати даних на UDP, перш ніж перейти на TCP |
| `tcp-timeout` | uint64 | 20000000 мкс = **20 с** | таймаут операцій керувального з'єднання; `0` — вимкнено |
| `retry` | uint | 20 | скільки разів пробувати зайняти пару портів під RTP/RTCP |
| `udp-reconnect` | bool | true | перепідключатися, якщо сервер закрив RTSP, поки йде UDP-потік |
| `teardown-timeout` | uint64 | 100000000 нс = 100 мс | скільки часу дати на `TEARDOWN` під час зупинки |
| `udp-buffer-size` | int | 524288 | `SO_RCVBUF` внутрішніх `udpsrc` |
| `port-range` | string | NULL | `"5000-5010"` — звузити клієнтські порти під дірку у фаєрволі |
| `probation` | uint | 2 | скільки пакетів поспіль треба, щоб визнати нове джерело |
| `do-rtsp-keep-alive` | bool | true | підтримувати сеанс живим між командами |
| `rtp-blocksize` | uint | 0 | попросити сервер різати пакети до такого розміру |
| `short-header` | bool | false | мінімальний набір заголовків — для серверів, що давляться довгими |
| `connection-speed` | uint64 | 0 | підказка серверові про швидкість каналу, кбіт/с |
| `is-live` | bool | true | поводитися як живе джерело |
| `user-id`, `user-pw` | string | NULL | облікові дані окремо від URL |
| `onvif-mode`, `backchannel` | bool, enum | false, `none` | поведінка клієнта ONVIF і зворотний звуковий канал |
| `tls-validation-flags` | flags | перевіряти все | що саме перевіряти в сертифікаті для `rtsps://` |
| `debug` | bool | false | друкувати обмін RTSP у журнал |

Значення `2000` у `latency` — не описка й не консерватизм: це число для перегляду запису з сервера через інтернет. Для лінка в межах кімнати чи борта його ставлять у 50–200 мс.

Друга несподіванка — `do-retransmission=true`. У самому `rtpjitterbuffer` та сама властивість типово вимкнена; `rtspsrc` вмикає її за вас, бо в сеансі RTSP є зворотний канал і сервер, який зазвичай уміє повторювати. Наслідок: зменшуючи `latency` до ста мілісекунд, ви заодно вбиваєте повтори — вікно стає коротшим за час обміну туди-назад, і пакет-повтор просто не встигає.

Режими `buffer-mode` — це той самий перелік, що й у буфера джитера, плюс `auto`. `auto` вибирає `buffer`, коли сеанс має скінченну тривалість і контейнерний потік (тобто це запис на сервері), і `slave` в усіх інших випадках — жива камера завжди потрапляє в `slave`.

### Що саме передається всередину

| Властивість `rtspsrc` | Куди йде |
|---|---|
| `latency`, `drop-on-latency`, `do-retransmission`, `ntp-sync`, `buffer-mode`, `max-rtcp-rtp-time-diff` | менеджер сеансу `rtpbin` → його буфери джитера |
| `udp-buffer-size`, `multicast-iface` | внутрішні `udpsrc` |
| `probation` | сесія RTP усередині `rtpbin` |
| `rtp-blocksize`, `connection-speed`, `port-range` | заголовки запиту `SETUP`, тобто прохання до сервера |

Решти властивостей буфера джитера в `rtspsrc` немає взагалі. Дорога до них — сигнал `new-manager`, а далі сигнал `rtpbin` про кожен створений буфер.

### Сигнали

| Сигнал | Сигнатура | Навіщо |
|---|---|---|
| `pad-added` | `void (GstElement *src, GstPad *pad, gpointer u)` | пад під конкретний потік нарешті з'явився |
| `no-more-pads` | `void (GstElement *src, gpointer u)` | падів більше не буде — сеанс описано повністю |
| `select-stream` | `gboolean (GstRTSPSrc *src, guint num, GstCaps *caps, gpointer u)` | `FALSE` — не робити `SETUP` для цього потоку взагалі |
| `on-sdp` | `void (GstRTSPSrc *src, GstSDPMessage *sdp, gpointer u)` | подивитися й підправити SDP до того, як його вжито |
| `before-send` | `gboolean (GstRTSPSrc *src, GstRTSPMessage *msg, gpointer u)` | додати заголовок у запит; `FALSE` — не слати його зовсім |
| `new-manager` | `void (GstRTSPSrc *src, GstElement *manager, gpointer u)` | дістатися до внутрішнього `rtpbin` |
| `handle-request` | `void (GstRTSPSrc *src, GstRTSPMessage *req, GstRTSPMessage *resp, gpointer u)` | відповісти на запит, що прийшов від сервера |
| `request-rtcp-key` | `GstCaps* (GstRTSPSrc *src, guint session, gpointer u)` | віддати ключі для захищеного RTCP |
| `accept-certificate` | `gboolean (GstRTSPSrc *src, GTlsConnection *conn, GTlsCertificate *peer, GTlsCertificateFlags errors, gpointer u)` | вирішити долю сумнівного сертифіката `rtsps://` |

Два з них вирішують типову задачу «взяти з камери лише відео» краще, ніж перевірка caps у `pad-added`: `select-stream` відсіює потік ще до `SETUP`, тобто камера навіть не почне слати звук, і мережа не носитиме зайвого.

```c
static gboolean
select_stream (GstElement * src, guint num, GstCaps * caps, gpointer user_data)
{
  const GstStructure *s = gst_caps_get_structure (caps, 0);

  /* FALSE тут означає «не робити SETUP», а не «прийняти й викинути» */
  return g_strcmp0 (gst_structure_get_string (s, "media"), "video") == 0;
}

static void
on_pad_added (GstElement * src, GstPad * pad, gpointer depay)
{
  GstPad *sink = gst_element_get_static_pad (GST_ELEMENT (depay), "sink");

  if (!gst_pad_is_linked (sink))
    gst_pad_link (pad, sink);
  gst_object_unref (sink);
}

g_signal_connect (rtspsrc, "select-stream", G_CALLBACK (select_stream), NULL);
g_signal_connect (rtspsrc, "pad-added", G_CALLBACK (on_pad_added), depay);
```

Пади тут з'являються вже після `DESCRIBE`, тобто на переході в `PAUSED`, — це саме той випадок, задля якого існують [пади, що виникають на ходу](book:media-vision/pads-and-linking).

А ось дорога до налаштувань буфера джитера, яких `rtspsrc` не показує:

```c
static void
on_new_jitterbuffer (GstElement * rtpbin, GstElement * jb,
    guint session, guint ssrc, gpointer user_data)
{
  g_object_set (jb, "max-misorder-time", 500, "faststart-min-packets", 3, NULL);
}

static void
on_new_manager (GstElement * src, GstElement * manager, gpointer user_data)
{
  g_signal_connect (manager, "new-jitterbuffer",
      G_CALLBACK (on_new_jitterbuffer), NULL);
}
```

## rtpjitterbuffer: вікно очікування

| Властивість | Тип | Типово | Що робить |
|---|---|---|---|
| `latency` | uint | 200 мс | стала затримка, яку елемент додає потокові в обмін на право чекати |
| `mode` | enum | `slave` | звідки береться час на виході |
| `do-lost` | bool | false | слати вниз подію `GstRTPPacketLost`, коли вікно на пакет минуло |
| `drop-on-latency` | bool | false | викидати найстаріші пакети замість рости понад `latency` |
| `do-retransmission` | bool | false | просити повтор конкретного пакета вгору по конвеєру |
| `rtx-delay` | int | −1 | скільки чекати перед запитом повтору; −1 — за виміряним джитером |
| `rtx-min-delay` | uint | 0 мс | нижня межа для попереднього |
| `rtx-max-retries` | int | −1 | скільки разів просити той самий пакет; −1 — без обмеження |
| `rtx-retry-timeout` | int | −1 | скільки чекати відповіді до наступної спроби; −1 — за виміряним RTT |
| `rtx-retry-period` | int | −1 | загальний час спроб на один пакет; −1 — оцінка |
| `rtx-delay-reorder` | int | 3 | на скільки номерів має «обігнати» сусід, щоб пакет визнали зниклим |
| `rtx-next-seqnum` | bool | true | замовляти повтор і для ще не прострочених наступних номерів |
| `max-misorder-time` | uint | 2000 мс | наскільки давнім може бути пакет, щоб його ще прийняли |
| `max-dropout-time` | uint | 60000 мс | яка дірка в номерах ще вважається дірою, а не новим потоком |
| `max-rtcp-rtp-time-diff` | int | −1 (у `rtspsrc` — 1000 мс) | наскільки звіт RTCP може випереджати дані, щоб йому вірили |
| `ts-offset` | int64 | 0 нс | ручний зсув вихідних міток — для зведення двох джерел |
| `rfc7273-sync` | bool | false | синхронізувати за годинником, оголошеним у SDP (RFC 7273) |
| `faststart-min-packets` | uint | 0 | скільки поспіль пакетів дозволяють віддати перший кадр негайно; `0` — вимкнено |
| `percent` | int | — | лише читання: наповненість буфера у відсотках |
| `stats` | GstStructure | — | лише читання: лічильники (нижче) |

Режими виводу:

| `mode` | Число | Поведінка |
|---|---|---|
| `none` | 0 | нічого не переставляти й нічого не чекати; час беруть як є |
| `slave` | 1 | вимірювати розбіжність кварців відправника й приймача та повільно підлаштовувати свою шкалу |
| `buffer` | 2 | режим накопичення: буфер наповнюють до `latency`, повідомляючи про це `GST_MESSAGE_BUFFERING` |
| `synced` | 4 | брати відповідність «мітка RTP ↔ абсолютний час» зі звітів відправника RTCP |

Числа 3 в цьому переліку немає: воно зарезервоване, і саме під ним у `rtspsrc` живе його власне `auto`. Практичний вибір простий: одна камера — `slave`; два потоки з різних камер, які треба звести в один час, — `synced` і `do-rtcp=true`, бо без звітів відправника зводити нема за чим.

Поля структури `stats` — усі `guint64`, крім одного:

| Поле | Що рахує |
|---|---|
| `num-pushed` | пакетів віддано далі |
| `num-lost` | пакетів визнано втраченими (не прийшли до кінця вікна) |
| `num-late` | пакетів прийшло після свого вікна — тобто дарма |
| `num-duplicates` | дублікатів відкинуто |
| `avg-jitter` | згладжена оцінка джитера, наносекунди |
| `rtx-count` | скільки повторів замовлено |
| `rtx-success-count` | скільки з них прийшло вчасно |
| `rtx-per-packet` (double) | середнє число замовлень на один пакет |
| `rtx-rtt` | середній час обміну туди-назад за замовленнями повтору, наносекунди |

```c
GstStructure *stats = NULL;
guint64 pushed = 0, lost = 0, late = 0, dup = 0;

g_object_get (jitterbuffer, "stats", &stats, NULL);
gst_structure_get (stats,
    "num-pushed", G_TYPE_UINT64, &pushed,
    "num-lost", G_TYPE_UINT64, &lost,
    "num-late", G_TYPE_UINT64, &late,
    "num-duplicates", G_TYPE_UINT64, &dup, NULL);
gst_structure_free (stats);      /* структуру віддають у власність — звільняти обов'язково */
```

Два лічильники розрізняють два зовсім різні діагнози, і саме на цій різниці будують вибір `latency`.

**Умова: 10 хвилин потоку 1080p30, `latency = 200`, зі `stats` знято `num-pushed = 1072400`, `num-lost = 340`, `num-late = 1260`.**

```
усього пакетів      = 1072400 + 340 + 1260 = 1 074 000
частка запізнілих   = 1260 / 1074000 ≈ 0.00117 = 0.117 %
частка втрачених    = 340 / 1074000  ≈ 0.00032 = 0.032 %
```

Запізнілих учетверо більше, ніж по-справжньому втрачених. Означає це не погану мережу, а замале вікно: пакети доїжджають, просто пізніше, ніж їх ладні чекати. Зворотна картина — `num-late` близько нуля при помітному `num-lost` — каже, що збільшувати `latency` марно: те, що не прийшло, не прийде.

## Депейлоадери

| Елемент | Приймає (`application/x-rtp`) | Віддає | Стандарт |
|---|---|---|---|
| `rtph264depay` | `media=video, clock-rate=90000, encoding-name=H264` | `video/x-h264`: `stream-format=avc, alignment=au` або `stream-format=byte-stream, alignment=nal\|au` | RFC 6184 |
| `rtph265depay` | `media=video, clock-rate=90000, encoding-name=H265` | `video/x-h265`: `stream-format=hvc1, alignment=au` або `stream-format=byte-stream, alignment=nal\|au` | RFC 7798 |
| `rtpjpegdepay` | `media=video, clock-rate=90000, encoding-name=JPEG` або статичний `payload=26` | `image/jpeg` | RFC 2435 |

| Властивість | Тип | Типово | Є в | Що робить |
|---|---|---|---|---|
| `wait-for-keyframe` | bool | false | h264, h265 (з 1.20) | після втрати мовчати, доки не прийде цілий ключовий кадр |
| `request-keyframe` | bool | false | h264, h265 (з 1.20) | після втрати ще й попросити ключовий кадр негайно — подією вгору по конвеєру |

Обидві властивості мають сенс лише разом із `do-lost=true` на буфері джитера: без події про втрату депейлоадер помічає дірку аж на стрибку номера, тобто із запізненням на цілий пакет. `request-keyframe` доходить до камери через RTCP, і виконують його не всі камери — прохання, а не команда.

У `rtpjpegdepay` таких властивостей немає, і це не недогляд: кожен кадр [motion JPEG](book:algorithms/jpeg-intra) самодостатній, тож «наступний ключовий» тут — просто наступний кадр.

Який саме `stream-format` вибере депейлоадер, вирішує не він, а домовленість із наступним елементом. Коли треба напевно — ставлять фільтр:

```sh
rtph264depay ! video/x-h264,stream-format=byte-stream,alignment=au ! h264parse ! ...
```

Байтовий потік із стартовими кодами `00 00 00 01` перед кожною [NAL-одиницею](book:algorithms/h264-nal-structure) — це те, чого чекають більшість декодерів і парсерів; формат `avc` із префіксами довжини потрібен, коли далі пишуть у контейнер MP4.

## caps application/x-rtp

Це опис, який `udpsrc` оголошує, а депейлоадер читає. Обов'язкові поля — перші чотири; без них ланцюг не постане.

| Поле | Тип | Приклад | Значення |
|---|---|---|---|
| `media` | string | `video` | `video`, `audio`, `application`, `text` |
| `payload` | int | `96` | номер типу навантаження, 0–127; динамічні — від 96 |
| `clock-rate` | int | `90000` | частота лічильника міток RTP; для відео майже завжди 90 кГц |
| `encoding-name` | string | `H264` | назва кодека великими літерами, як у `a=rtpmap` |
| `encoding-params` | string | `2` | для звуку — число каналів |
| `ssrc` | uint | `1234567` | очікуване джерело; зайве для звичайного приймання |
| `timestamp-offset`, `seqnum-offset` | uint | — | початкові значення, коли вони відомі наперед |
| `a-framerate` | string | `30` | частота кадрів із рядка `a=framerate` |
| `npt-start`, `npt-stop`, `play-speed`, `play-scale` | — | — | позиція й швидкість відтворення; заповнює `rtspsrc` із відповіді на `PLAY` |
| `packetization-mode` | string | `1` | H.264: чи дозволено фрагменти й агрегати |
| `profile-level-id` | string | `640028` | H.264: профіль і рівень, як у SDP |
| `sprop-parameter-sets` | string | `Z0LgHtoCgPRA,aM4wpIA=` | H.264: SPS і PPS у base64, через кому |
| `sprop-vps`, `sprop-sps`, `sprop-pps` | string | — | H.265: те саме трьома окремими полями |

Мінімальний опис, з яким `udpsrc` віддає потік депейлоадерові:

```sh
gst-launch-1.0 -v \
  udpsrc port=5600 caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264,payload=(int)96" \
  ! rtpjitterbuffer latency=100 do-lost=true \
  ! rtph264depay wait-for-keyframe=true ! h264parse ! avdec_h264 ! autovideosink sync=false
```

Типи в дужках тут не прикраса. Поля, що прийшли з `a=fmtp`, — **завжди рядки**, і депейлоадер читає їх саме як рядки. Написане без `(string)` числоподібне значення стане цілим числом і для елемента просто зникне: `profile-level-id=640028` — це число, `profile-level-id=(string)640028` — те, що потрібно. Найдорожче це коштує на `sprop-parameter-sets`: без нього декодер чекатиме, доки параметри прийдуть у самому потоці.

## SDP → caps: правило переведення

![Ліворуч рядки SDP, праворуч відповідні поля caps application/x-rtp, між ними стрілки; унизу застереження про типи](img/sdp-to-caps.svg)

*Кожне поле caps приходить із конкретного рядка; адреса й порт — єдине, що в caps не потрапляє.*

Переведенням займаються дві функції: `gst_sdp_media_get_caps_from_media()` бере основу, `gst_sdp_media_attributes_to_caps()` додає решту атрибутів (і лише вона ставить `extmap`, `ssrc` і `rid`). Правила такі:

| Рядок SDP | Поля caps |
|---|---|
| `m=video 0 RTP/AVP 96` | `media=(string)video`, `payload=(int)96` |
| `a=rtpmap:96 H264/90000` | `encoding-name=(string)H264`, `clock-rate=(int)90000` |
| `a=rtpmap:97 OPUS/48000/2` | те саме плюс `encoding-params=(string)2` |
| `a=fmtp:96 ключ=значення;ключ=значення` | кожна пара — окреме поле-рядок |
| `a=framesize:96 1280-720` | `width=(int)1280`, `height=(int)720` |
| `a=framerate:30` | `a-framerate=(string)30` |
| будь-який інший `a=ключ:значення` | поле `a-ключ` |
| `c=`, порт із `m=` і з відповіді на `SETUP` | у caps не потрапляють — це адреса й порти сокетів |

Ось чому `rtspsrc` не треба нічого підказувати, а `udpsrc` треба підказувати все: обидва врешті працюють з тим самим описом, просто перший добуває його з [SDP](book:communications/rtsp-sdp) сам, а другому ви пишете його руками. Знявши SDP один раз (`gst-launch-1.0 -v rtspsrc location=… ` друкує caps кожного паду), решту життя можна ганяти той самий потік голим `udpsrc` — рядок caps просто копіюють із виводу.

## Транспорт RTSP

Дозволені транспорти перелічує `protocols`; у командному рядку значення складають знаком `+`.

| Значення | Що означає |
|---|---|
| `udp` | одноадресний RTP по UDP, окремі порти |
| `udp-mcast` | багатоадресний RTP по UDP |
| `tcp` | RTP усередині керувального з'єднання (interleaved) |
| `http` | тунель RTSP крізь HTTP — для мереж, де відкрито лише 80/443 |
| `tls` | керувальний канал під TLS, схема `rtsps://` |

Домовляються про транспорт у запиті `SETUP`, і виглядає ця домовленість як один заголовок:

| Заголовок `Transport` | Що з нього випливає |
|---|---|
| `RTP/AVP;unicast;client_port=5000-5001` | звичайний UDP; `RTP/AVP` без третьої частини означає саме UDP |
| `RTP/AVP/UDP;unicast;client_port=5000-5001` | те саме, записане явно |
| `RTP/AVP;multicast;destination=239.1.2.3;port=5000-5001;ttl=16` | група, спільна для всіх приймачів |
| `RTP/AVP/TCP;unicast;interleaved=0-1` | RTP і RTCP усередині вже відкритого TCP-з'єднання |

У відповіді сервер повторює рядок і додає своє: `server_port=`, `source=`, `ssrc=`. Парність портів не випадкова — RTP займає парний, RTCP наступний за ним непарний; те саме правило діє й для номерів каналів у interleaved, де RTP іде каналом 0, а RTCP — каналом 1. Ця пара — прямий наслідок того, як [RTP і RTCP](book:communications/rtp-rtcp) ділять сеанс.

![Угорі RTP-пакет у власній датаграмі UDP; унизу той самий пакет усередині TCP з префіксом «долар, канал, довжина»](img/interleaved-frame.svg)

*У датаграмі межу пакета задає сама датаграма; у потоці TCP її доводиться позначати двома байтами довжини.*

Interleaved-обгортка описана в RFC 2326 §10.12 і складається з чотирьох байтів перед пакетом: `$` (0x24), номер каналу, і два байти довжини, старший перший. Звідси дві практичні межі. По-перше, пакет не може бути довшим за 65535 байтів. По-друге, керування й медіа тепер їдуть одним з'єднанням — затор через один великий кадр затримує й команди RTSP, і навпаки; звідси характерна для TCP-режиму «гумова» затримка, що росте на заторі й ніколи сама не спадає.

## Мінімальні робочі рядки

```sh
# 1. Одноадресний UDP, живий лінк: маленьке вікно, облік втрат, тиша замість зелених квадратів
gst-launch-1.0 -v \
  udpsrc port=5600 buffer-size=524288 \
    caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264,payload=(int)96" \
  ! rtpjitterbuffer latency=100 do-lost=true drop-on-latency=true \
  ! rtph264depay wait-for-keyframe=true ! h264parse ! avdec_h264 ! autovideosink sync=false

# 2. Багатоадресна група на машині з кількома мережами
gst-launch-1.0 -v \
  udpsrc address=239.1.2.3 port=5600 multicast-iface=eth1 auto-multicast=true \
    caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264,payload=(int)96" \
  ! rtpjitterbuffer latency=200 ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink

# 3. RTSP із камери, налаштований на свіжість, а не на плавність
gst-launch-1.0 -v \
  rtspsrc location=rtsp://user:pass@192.168.1.64:554/Streaming/Channels/101 \
          latency=100 protocols=udp timeout=2000000 \
  ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false

# 4. Той самий потік крізь NAT: транспорт зафіксовано, UDP не пробують узагалі
gst-launch-1.0 -v \
  rtspsrc location=rtsp://192.168.1.64:554/Streaming/Channels/101 \
          latency=300 protocols=tcp \
  ! decodebin ! autovideosink
```

Різниця між третім і четвертим рядками — не в смаку, а в діагнозі. Якщо `protocols=udp` дає тишу, а `protocols=tcp` — стабільну картинку, справа не в GStreamer і не в камері: між ними стоїть щось, що не пускає вхідні датаграми, і далі йти треба до [NAT](book:communications/nat), а не до властивостей елементів.
