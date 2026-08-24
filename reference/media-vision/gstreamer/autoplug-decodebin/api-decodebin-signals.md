# 📋 Керування автодобором: властивості, сигнали, вибір потоків

Тут зібрано весь інтерфейс, яким програма втручається в автодобір: властивості `decodebin` із типами й типовими значеннями, сім його сигналів із точними підписами, моментом виклику й — що гублять найчастіше — поведінкою, коли обробників на сигнал кілька; далі інтерфейс `decodebin3` і `uridecodebin3`, де потоки вибирають уже не сигналом, а повідомленням і подією; і насамкінець два важелі, що діють поза елементом: ранг фабрики та розбір повідомлення про брак кодека. Звірено з чинною гілкою GStreamer 1.x за довідкою плагіна `playback` і за джерелами `gst/playback/gstdecodebin2.c` та `gstdecodebin3.c`; де можливість з'явилася пізніше за 1.0, стоїть позначка «з 1.x».

Ці елементи живуть не в ядрі, а в плагіні `playback` із набору gst-plugins-base, тож окремого заголовка не мають — усе доступне через звичайний `gst.h`, а властивості й сигнали адресують за іменами:

```c
#include <gst/gst.h>
#include <gst/pbutils/pbutils.h>   /* потрібен лише для розбору missing-plugin */
```

```
gcc app.c -o app $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-pbutils-1.0)
```

## Властивості `decodebin`

| властивість | тип | типове | що робить |
|---|---|---|---|
| `caps` | `GstCaps *` | перелік сирих форматів (нижче) | цільові caps: де добір зупиняється |
| `sink-caps` | `GstCaps *` | `EMPTY` | caps вхідних даних; задано → `typefind` не створюють узагалі |
| `expose-all-streams` | `gboolean` | `TRUE` | виставляти назовні й ті потоки, які не дійшли до цільових caps або лишилися невпізнаними |
| `force-sw-decoders` | `gboolean` | `FALSE` | не брати фабрик, позначених як апаратні |
| `use-buffering` | `gboolean` | `FALSE` | постити `GST_MESSAGE_BUFFERING` за наповненням внутрішніх черг |
| `low-percent` | `gint` | 10 | нижній поріг у відсотках: нижче нього буферизація починається |
| `high-percent` | `gint` | 99 | верхній поріг: на ньому буферизація вважається завершеною |
| `max-size-bytes` | `guint` | 0 (авто) | межа черги в байтах |
| `max-size-buffers` | `guint` | 0 (авто) | межа черги в буферах |
| `max-size-time` | `guint64` | 0 (авто) | межа черги в наносекундах |
| `post-stream-topology` | `gboolean` | `FALSE` | постити повідомлення `stream-topology` на кожну зміну графа |
| `connection-speed` | `guint64` | 0 (невідомо) | швидкість каналу в кбіт/с — підказка для демультиплексорів адаптивного мовлення |
| `subtitle-encoding` | `gchararray` | `NULL` | кодування, яке припускати для субтитрів не в UTF-8 |

Типове значення `caps` — це і є вбудоване визначення слова «декодовано»:

```
video/x-raw(ANY); audio/x-raw(ANY); text/x-raw(ANY);
subpicture/x-dvd; subpicture/x-dvb; subpicture/x-xsub; subpicture/x-pgs;
closedcaption/x-cea-608; closedcaption/x-cea-708;
application/x-onvif-metadata; meta/x-klv; meta/x-id3; meta/x-st-2038
```

Три властивості з цієї таблиці мають наслідки, ширші за їхній опис, і саме на них будують більшість втручань.

**`caps` і `expose-all-streams` працюють у парі.** Перша каже, де зупинитися; друга — що робити з гілкою, яка до цієї зупинки не дійшла. Типово `expose-all-streams=TRUE`, і назовні виходить усе, включно з потоком, для якого декодера не знайшлося: пад буде, а на ньому — не сирі кадри, а те, до чого вдалося дійти. Значення `FALSE` викидає такі гілки мовчки, і це рівно те, що потрібно, коли з файлу беруть лише відео й не хочуть чекати на екзотичну доріжку метаданих.

**`sink-caps` вимикає розпізнавання, а не пришвидшує його.** Задавши сюди `video/quicktime`, ви не підказуєте `typefind` відповідь — ви скасовуєте його створення. Разом із ним зникає й потреба накопичити початковий шматок потоку, тож на джерелі, яке віддає байти повільно, це прямий виграш у затримці до першого кадру. Ціна відповідна: помилилися з типом — добір піде хибною гілкою й нікуди не прийде.

**Чотири властивості черг — це властивості внутрішнього `multiqueue`.** `max-size-*` і пара `low-percent`/`high-percent` просто прокидаються в нього. Нуль в `max-size-*` означає не «нескінченно», а «вирішуй сам»: `decodebin` ставить власні початкові межі й піднімає їх, коли якась гілка застрягає й перемежування доріжок вимагає більшого запасу.

> [Затримка й буферизація в конвеєрі](topic:media-vision/latency-and-buffering) — `BUFFERING`-повідомлення несе відсоток наповнення, і конвеєр на час накопичення тримають у PAUSED. Пороги `low-percent`/`high-percent` задають, коли починати й коли припиняти цю паузу.

## Сигнали `decodebin`

Усі сім оголошено з прапорцем `G_SIGNAL_RUN_LAST`. Це не дрібниця: обробник, під'єднаний звичайним `g_signal_connect()`, виконується **перед** типовим обробником самого елемента, а `g_signal_connect_after()` — після нього.

| сигнал | повертає | коли викликають |
|---|---|---|
| `autoplug-continue` | `gboolean` | на кожних нових caps, **перед** тим як шукати для них елементи |
| `autoplug-factories` | `GValueArray *` | коли потрібен список сумісних фабрик для цих caps |
| `autoplug-sort` | `GValueArray *` | після того, як список зібрано, — щоб переставити або відсіяти |
| `autoplug-select` | `GstAutoplugSelectResult` | на **кожну** фабрику зі списку, перед спробою її створити |
| `autoplug-query` | `gboolean` | коли дібраний елемент шле запит, на який `decodebin` сам не відповідає |
| `unknown-type` | `void` | коли пад додано, а продовжувати добір нема чим |
| `drained` | `void` | коли всі дані пройшли й декодувати більше нічого |

```c
gboolean   autoplug_continue_cb  (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  gpointer user_data);

GValueArray *autoplug_factories_cb (GstElement *bin, GstPad *pad, GstCaps *caps,
                                    gpointer user_data);

GValueArray *autoplug_sort_cb    (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  GValueArray *factories, gpointer user_data);

GstAutoplugSelectResult
           autoplug_select_cb    (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  GstElementFactory *factory, gpointer user_data);

gboolean   autoplug_query_cb     (GstElement *bin, GstPad *pad, GstElement *child,
                                  GstQuery *query, gpointer user_data);

void       unknown_type_cb       (GstElement *bin, GstPad *pad, GstCaps *caps,
                                  gpointer user_data);

void       drained_cb            (GstElement *bin, gpointer user_data);
```

Три слова відповіді `autoplug-select` — це перелічуваний тип із плагіна `playback`:

```c
typedef enum {
  GST_AUTOPLUG_SELECT_TRY    = 0,   /* створити цей елемент і спробувати */
  GST_AUTOPLUG_SELECT_EXPOSE = 1,   /* нічого не ставити, виставити пад як є */
  GST_AUTOPLUG_SELECT_SKIP   = 2    /* пропустити фабрику, взяти наступну */
} GstAutoplugSelectResult;
```

Різниця між `SKIP` і `EXPOSE` — це різниця між «не цим» і «взагалі нічим». `SKIP` рухає перебір далі по списку, `EXPOSE` перебір закінчує й віддає пад назовні з нинішніми caps, хай навіть це стиснутий потік.

### Типові обробники

Знати, що станеться без вашого втручання, потрібно рівно для того, щоб зрозуміти, від чого ви відхиляєтеся.

| сигнал | що робить типовий обробник |
|---|---|
| `autoplug-continue` | завжди `TRUE` — добір триває |
| `autoplug-factories` | бере з реєстру всі фабрики виду `GST_ELEMENT_FACTORY_TYPE_DECODABLE` з рангом від `GST_RANK_MARGINAL`, відсіює за caps на sink-боці й повертає впорядкованими за спаданням рангу |
| `autoplug-sort` | `NULL` — порядок лишається як був |
| `autoplug-select` | завжди `GST_AUTOPLUG_SELECT_TRY` |
| `autoplug-query` | `FALSE` — запит не оброблено |

У відсіві за caps є деталь, яку варто прочитати уважно: суворість перевірки залежить від самих caps. Типовий обробник кличе `gst_element_factory_list_filter (…, GST_PAD_SINK, gst_caps_is_fixed (caps))` — тобто вимагає повного вкладення caps у шаблон лише тоді, коли caps **зафіксовані**. Поки формат ще неповний, вистачає непорожнього перерізу, інакше на ранньому кроці повідпадали б усі придатні кандидати.

Список кандидатів `decodebin` кешує й перебудовує не щоразу, а лише коли змінився лічильник змін реєстру — те саме число-cookie, яким користуються всі, хто тримає в себе відібраний зріз реєстру.

> [Модель плагінів і реєстр елементів](topic:media-vision/plugin-model) — фабрика як паспорт елемента: категорія `klass`, шаблонні caps і ранг лежать у реєстрі без завантаження коду плагіна. Маска `GST_ELEMENT_FACTORY_TYPE_DECODABLE` — це об'єднання бітів `DECODER | DEMUXER | DEPAYLOADER | PARSER | DECRYPTOR`.

### Що буде, коли обробників кілька

Ось те, чого не видно з підписів і що ламає програму найтихіше. Кожен із сигналів, що повертають значення, має **накопичувач** — функцію, яка вирішує, чи кликати наступного обробника й що вважати остаточною відповіддю. Накопичувачі тут різні, і два з них влаштовані **протилежно**.

| сигнал | накопичувач | поведінка з кількома обробниками |
|---|---|---|
| `autoplug-continue` | `_gst_boolean_accumulator` | ланцюжок триває, **поки повертають `TRUE`**; перший `FALSE` зупиняє емісію й стає результатом |
| `autoplug-select` | `_gst_select_accumulator` | ланцюжок триває, **поки повертають `TRY`**; перший `SKIP` або `EXPOSE` зупиняє емісію й стає результатом |
| `autoplug-factories` | `_gst_array_accumulator` | результатом стає відповідь **першого** обробника, далі емісію припиняють |
| `autoplug-sort` | `_gst_array_hasvalue_accumulator` | ланцюжок триває, поки повертають `NULL`; перший непорожній масив стає результатом |
| `autoplug-query` | `_gst_boolean_or_accumulator` | кличуть **усіх**, результат — логічне «або» всіх відповідей |

З цієї таблиці випливають три практичні наслідки.

Перший: `autoplug-continue` і `autoplug-select` мають дзеркальні умови продовження. У першому «так» означає «питайте далі», у другому «так» (тобто `TRY`) означає те саме — але перекласти звичку з одного на інший не вийде, бо `TRY` — це не `TRUE`, а нуль перелічуваного типу.

Другий: ваш обробник, під'єднаний звичайним `g_signal_connect()`, здатен **зовсім не дати виконатися типовому**. Повернули `FALSE` з `autoplug-continue` — типовий обробник, який повернув би `TRUE`, уже не покличуть; повернули `SKIP` — та сама історія. Це не збій, а спосіб, у який втручання взагалі працює.

Третій: на `autoplug-factories` другий обробник у процесі — мертвий код. Якщо дві бібліотеки в одному застосунку під'єднаються до цього сигналу, працюватиме та, що встигла перша.

> [GObject: об'єктна система, на якій стоїть GStreamer](topic:media-vision/gobject-basics) — сигнал як точка розширення класу: обробники зберігаються списком, накопичувач збирає з їхніх повернень одну відповідь, а прапорець `RUN_FIRST`/`RUN_LAST` визначає, де в цьому списку стоїть типовий обробник самого класу.

### Потік виконання

Усі `autoplug-*`, а також `unknown-type` і `drained`, видають **із потоку даних** `decodebin` — того самого, що читає файл і штовхає буфери, — а не з головного потоку програми. Звідси три обмеження, порушення яких дає або зависання, або падіння без зрозумілого сліду:

- нічого малювати й нічого чіпати в інтерфейсі користувача прямо з обробника;
- не блокуватися надовго: доки обробник не повернувся, конвеєр на цій гілці стоїть;
- не переводити конвеєр у інший стан зсередини обробника — `gst_element_set_state()` на весь конвеєр звідси приводить до взаємного блокування.

Звичайний спосіб обійти все три — покласти рішення в чергу й повернутися, а власне дію зробити в головному циклі.

> [Потоки виконання й черги: де конвеєр міняє потік](topic:media-vision/threads-and-queues) — потік даних належить елементові, що штовхає буфери, і всі зворотні виклики вздовж його шляху виконуються в ньому ж. Головний потік програми з ним не збігається.

### `GValueArray`: як із ним поводитися

Два сигнали оперують `GValueArray` — типом, який у GLib позначено застарілим ще з 2.32, але який лишається в цьому інтерфейсі заради сумісності. Кожен елемент масиву — `GValue` типу `G_TYPE_OBJECT`, усередині якого лежить `GstElementFactory *`.

```c
static GValueArray *
on_autoplug_sort (GstElement *bin, GstPad *pad, GstCaps *caps,
                  GValueArray *factories, gpointer user_data)
{
  GValueArray *result = g_value_array_new (factories->n_values);

  /* пропускаємо все, що зареєстроване як апаратне, а решту лишаємо як є */
  for (guint i = 0; i < factories->n_values; i++) {
    GValue *v = g_value_array_get_nth (factories, i);
    GstElementFactory *f = GST_ELEMENT_FACTORY (g_value_get_object (v));

    if (gst_element_factory_list_is_type (f,
            GST_ELEMENT_FACTORY_TYPE_HARDWARE))
      continue;

    g_value_array_append (result, v);
  }

  return result;               /* володіння переходить до decodebin */
}
```

Вхідний масив належить тому, хто його дав, і чіпати його не можна — повертають **новий**. Повернений масив забирає `decodebin` і звільняє сам. Через застарілість типу цей сигнал майже недоступний із мов-обгорток: у GObject Introspection `GValueArray` не описано як слід, тож із Python практичний важіль — не `autoplug-factories`/`autoplug-sort`, а `autoplug-select`, де жодних масивів немає.

### `autoplug-query` — про що це насправді

Сигнал видають, коли **дібраний елемент** послав запит угору за течією, а `decodebin` не має чим відповісти. Найчастіший випадок — запит розподілу пам'яті (`GST_QUERY_ALLOCATION`), яким декодер питає, чи погодиться приймач на буфери певного виду. Всередині `decodebin` вище за декодером стоїть демультиплексор, який про приймачі нічого не знає, — тож без застосунку відповіді не буде, і декодер відкотиться на власні буфери, втративши передачу без копіювання.

Аргумент `child` каже, який саме внутрішній елемент питає, а `pad` — на якому паді. Обробник, який хоче відповісти, заповнює `query` і повертає `TRUE`.

> [Події й запити на падах](topic:media-vision/events-and-queries) — запит іде вздовж конвеєра синхронно й повертається з відповіддю в тій самій структурі; на відміну від події, запит має того, хто зобов'язаний відповісти.

## Сигнали біна: спіймати момент появи елемента

`decodebin` — бін, тож усе, що GStreamer дає для спостереження за вмістом біна, працює й тут. Це найпростіший спосіб виставити властивість дібраному елементові: іншої нагоди немає, бо ім'я елемента наперед невідоме.

```c
void element_added_cb        (GstBin *bin, GstElement *element,
                              gpointer user_data);
void element_removed_cb      (GstBin *bin, GstElement *element,
                              gpointer user_data);

/* з 1.10 — бачить і те, що додали у вкладені біни */
void deep_element_added_cb   (GstBin *bin, GstBin *sub_bin, GstElement *element,
                              gpointer user_data);
void deep_element_removed_cb (GstBin *bin, GstBin *sub_bin, GstElement *element,
                              gpointer user_data);
```

Пара з префіксом `deep-` (з 1.10) потрібна тоді, коли `decodebin` сидить усередині чогось іще — `uridecodebin`, `playbin` — і вішати сигнал на кожен внутрішній бін окремо незручно: `deep-element-added` на конвеєрі бачить усе, що з'явилося на будь-якій глибині.

```c
static void
on_deep_element_added (GstBin *pipeline, GstBin *sub_bin,
                       GstElement *element, gpointer user_data)
{
  GstElementFactory *f = gst_element_get_factory (element);   /* transfer none */
  if (f == NULL)
    return;

  const gchar *name = gst_plugin_feature_get_name (GST_PLUGIN_FEATURE (f));

  if (g_str_has_prefix (name, "avdec_"))
    g_object_set (element, "max-threads", 4, "output-corrupt", FALSE, NULL);
}
```

Сигнал видають **після** того, як елемент додано, але до того, як його перевели в робочий стан, — тобто властивості, які читають лише під час переходу станів, тут виставляти ще можна.

## `post-stream-topology`: подивитися на побудований граф

Увімкнена властивість змушує `decodebin` постити на шину повідомлення типу `GST_MESSAGE_ELEMENT` зі структурою на ім'я `stream-topology` щоразу, коли граф змінився. Поля структури:

| поле | тип | що в ньому |
|---|---|---|
| `caps` | `GstCaps` | формат на цій ланці |
| `pad` | `GstPad` | пад, від якого ланка починається |
| `element-srcpad` | `GstPad` | вихідний пад ланки; є лише там, де ланка закінчується виставленим падом |
| `next` | структура або список структур | наступна ланка; список — там, де гілка розгалужується |

Структура рекурсивна, тож розбирати її вручну варто лише тоді, коли це потрібно програмі. Щоб просто подивитися, вистачає одного рядка на шині:

```c
if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ELEMENT &&
    gst_message_has_name (msg, "stream-topology")) {
  gchar *s = gst_structure_to_string (gst_message_get_structure (msg));
  g_print ("%s\n", s);
  g_free (s);
}
```

> [Шина повідомлень: події й помилки конвеєра](topic:media-vision/bus-and-messages) — повідомлення `ELEMENT` несе довільну структуру від конкретного елемента; ім'я структури й розрізняє такі повідомлення між собою.

## `decodebin3` і `uridecodebin3`

Інтерфейс тут інший не косметично, а по суті: сигналів автодобору немає взагалі. Уся точка втручання — вибір потоків, і робиться він повідомленням і подією, а не зворотним викликом.

`decodebin3` має **одну** власну властивість:

| властивість | тип | типове |
|---|---|---|
| `caps` | `GstCaps *` | той самий перелік сирих форматів, що й у `decodebin` |

Пади: постійний `sink`, додаткові `sink_%u` на запит (для паралельних допоміжних потоків — наприклад, окремого файлу субтитрів), а назовні — `audio_%u`, `video_%u`, `text_%u`, `metadata_%u`.

Сигналів два:

```c
/* 1 — брати потік, 0 — не брати, −1 — вирішуй сам */
gint select_stream_cb    (GstElement *decodebin, GstStreamCollection *collection,
                          GstStream *stream, gpointer user_data);

void about_to_finish_cb  (GstElement *decodebin, gpointer user_data);
```

`select-stream` видають тоді, коли `decodebin3` вирішує, чи виставляти потік із колекції. Довідка прямо називає цей сигнал не основним шляхом: рекомендований спосіб — слухати `GST_MESSAGE_STREAM_COLLECTION` на шині й надсилати подію `GST_EVENT_SELECT_STREAMS`. Причина проста: сигнал видають із потоку даних і на кожен потік окремо, а подія дозволяє висловити вибір **цілим набором** і в будь-який момент, а не лише під час побудови.

`about-to-finish` означає «дані обраного URI повністю прочитано, тепер безпечно назвати наступний» — це механізм безшовної зміни джерела, і власне зміну роблять прямо з обробника.

`uridecodebin3` додає до цього роботу з URI й мережевим запасом:

| властивість | тип | типове |
|---|---|---|
| `uri` | `gchararray` | `NULL` |
| `suburi` | `gchararray` | `NULL` |
| `current-uri` | `gchararray` | `NULL` (лише читання за змістом) |
| `current-suburi` | `gchararray` | `NULL` |
| `caps` | `GstCaps *` | перелік сирих форматів |
| `use-buffering` | `gboolean` | `FALSE` |
| `buffer-size` | `gint` | −1 (авто) |
| `buffer-duration` | `gint64` | −1 (авто; у згенерованій довідці показано як `18446744073709551615`) |
| `download` | `gboolean` | `FALSE` |
| `download-dir` | `gchararray` | `NULL` |
| `ring-buffer-max-size` | `guint64` | 0 |
| `connection-speed` | `guint64` | 0 |
| `instant-uri` | `gboolean` | `FALSE` |

Сигнали ті самі два плюс третій:

```c
void source_setup_cb (GstElement *bin, GstElement *source, gpointer user_data);
```

Його видають, коли елемент-джерело вже створено, але ще не запущено, — єдина нагода виставити йому щось на кшталт `latency` в `rtspsrc` або власних заголовків HTTP.

`instant-uri=TRUE` (з 1.22) міняє сенс запису в `uri`: замість «наступний після завершення нинішнього» — «перемкнутися негайно».

## Колекція потоків: типи, прапорці, функції розбору

```c
guint         gst_stream_collection_get_size        (GstStreamCollection *collection);
/* transfer none — колекція лишається власником */
GstStream *   gst_stream_collection_get_stream      (GstStreamCollection *collection,
                                                     guint index);
const gchar * gst_stream_collection_get_upstream_id (GstStreamCollection *collection);

/* усе про один потік */
const gchar * gst_stream_get_stream_id    (GstStream *stream);   /* transfer none */
GstStreamType gst_stream_get_stream_type  (GstStream *stream);
GstCaps *     gst_stream_get_caps         (GstStream *stream);   /* transfer full */
GstTagList *  gst_stream_get_tags         (GstStream *stream);   /* transfer full */
GstStreamFlags gst_stream_get_stream_flags (GstStream *stream);

const gchar * gst_stream_type_get_name    (GstStreamType stype);
```

`GstStreamType` — набір бітів, а не одне значення; довідка окремо застерігає не покладатися на те, що там стоїть рівно один біт.

| стала | значення |
|---|---|
| `GST_STREAM_TYPE_UNKNOWN` | 1 |
| `GST_STREAM_TYPE_AUDIO` | 2 |
| `GST_STREAM_TYPE_VIDEO` | 4 |
| `GST_STREAM_TYPE_CONTAINER` | 8 |
| `GST_STREAM_TYPE_TEXT` | 16 |
| `GST_STREAM_TYPE_METADATA` | 32 |

`GstStreamFlags` (з 1.2) несе те, що про потік каже сам контейнер, — і саме цим користується типова поведінка, коли застосунок не вибрав нічого:

| стала | значення | що означає |
|---|---|---|
| `GST_STREAM_FLAG_NONE` | 0 | нічого особливого |
| `GST_STREAM_FLAG_SPARSE` | 1 | розріджений потік: дані йдуть нерівномірно, з великими проміжками (типово субтитри) |
| `GST_STREAM_FLAG_SELECT` | 2 | демультиплексор радить брати цей потік типово |
| `GST_STREAM_FLAG_UNSELECT` | 4 | брати лише на явну вимогу — доріжка коментарів режисера, звук для людей із вадами слуху |

Повідомлення й події, якими це все передають:

| що | тип | напрямок |
|---|---|---|
| `GST_MESSAGE_STREAM_COLLECTION` | повідомлення на шині | від елемента до застосунку |
| `GST_EVENT_STREAM_COLLECTION` | подія | **униз** за течією, серіалізована, липка |
| `GST_EVENT_SELECT_STREAMS` | подія | **угору** за течією |
| `GST_MESSAGE_STREAMS_SELECTED` | повідомлення на шині | підтвердження: ось що справді обрано |

```c
/* transfer full у вихідному аргументі — знімати посилання вам */
void      gst_message_parse_stream_collection      (GstMessage *message,
                                                    GstStreamCollection **collection);
void      gst_message_parse_streams_selected       (GstMessage *message,
                                                    GstStreamCollection **collection);
guint     gst_message_streams_selected_get_size    (GstMessage *message);
/* transfer full */
GstStream *gst_message_streams_selected_get_stream (GstMessage *message, guint idx);

/* streams — GList рядків-ідентифікаторів; подія копіює їх собі (з 1.10) */
GstEvent *gst_event_new_select_streams   (GList *streams);
void      gst_event_parse_select_streams (GstEvent *event, GList **streams);
```

Подію надсилають **конвеєрові**, а не окремому елементу: `GST_EVENT_SELECT_STREAMS` іде вгору за течією від кожного приймача, і саме так вона доходить до `decodebin3` незалежно від того, наскільки глибоко він захований.

## Мінімальний робочий виклик

Програма читає колекцію потоків, друкує її, вибирає перше відео й перший звук і надсилає вибір. Тут задіяно рівно той шлях, який довідка називає основним; `playbin3` узятий за найкоротшу оболонку — з `uridecodebin3` тіло обробника не змінюється жодним рядком.

```c
#include <gst/gst.h>

typedef struct {
  GMainLoop *loop;
  GstElement *pipeline;
  gboolean sent;
} App;

static gboolean
on_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  App *app = data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_STREAM_COLLECTION: {
      GstStreamCollection *coll = NULL;
      gst_message_parse_stream_collection (msg, &coll);      /* transfer full */
      if (coll == NULL)
        break;

      GList *wanted = NULL;
      gboolean have_video = FALSE, have_audio = FALSE;
      guint n = gst_stream_collection_get_size (coll);

      for (guint i = 0; i < n; i++) {
        GstStream *s = gst_stream_collection_get_stream (coll, i);  /* transfer none */
        GstStreamType t = gst_stream_get_stream_type (s);
        const gchar *id = gst_stream_get_stream_id (s);

        g_print ("%u  %-9s %s\n", i, gst_stream_type_get_name (t), id);

        if (t == GST_STREAM_TYPE_VIDEO && !have_video) {
          wanted = g_list_append (wanted, (gpointer) id);
          have_video = TRUE;
        } else if (t == GST_STREAM_TYPE_AUDIO && !have_audio) {
          wanted = g_list_append (wanted, (gpointer) id);
          have_audio = TRUE;
        }
      }

      if (wanted != NULL && !app->sent) {
        app->sent = TRUE;
        gst_element_send_event (app->pipeline,
            gst_event_new_select_streams (wanted));
      }

      g_list_free (wanted);          /* самі рядки належать колекції */
      gst_object_unref (coll);
      break;
    }

    case GST_MESSAGE_STREAMS_SELECTED: {
      guint n = gst_message_streams_selected_get_size (msg);
      g_print ("обрано %u:\n", n);
      for (guint i = 0; i < n; i++) {
        GstStream *s = gst_message_streams_selected_get_stream (msg, i); /* full */
        g_print ("   %s\n", gst_stream_get_stream_id (s));
        gst_object_unref (s);
      }
      break;
    }

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка: %s\n%s\n", err->message, dbg ? dbg : "");
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (app->loop);
      break;
    }

    case GST_MESSAGE_EOS:
      g_main_loop_quit (app->loop);
      break;

    default:
      break;
  }
  return TRUE;
}

int
main (int argc, char *argv[])
{
  gst_init (&argc, &argv);

  if (argc < 2) {
    g_printerr ("вжиток: %s <uri>\n", argv[0]);
    return 2;
  }

  App app = { 0, };
  app.loop = g_main_loop_new (NULL, FALSE);
  app.pipeline = gst_element_factory_make ("playbin3", "player");
  g_object_set (app.pipeline, "uri", argv[1], NULL);

  GstBus *bus = gst_element_get_bus (app.pipeline);
  gst_bus_add_watch (bus, on_bus, &app);
  gst_object_unref (bus);

  gst_element_set_state (app.pipeline, GST_STATE_PLAYING);
  g_main_loop_run (app.loop);

  gst_element_set_state (app.pipeline, GST_STATE_NULL);
  gst_object_unref (app.pipeline);
  g_main_loop_unref (app.loop);
  return 0;
}
```

**Вивід на файлі MKV з однією відео- і трьома звуковими доріжками:**

```
0  container  4b8a2f1c/00000000
1  video      4b8a2f1c/00000001
2  audio      4b8a2f1c/00000002
3  audio      4b8a2f1c/00000003
4  audio      4b8a2f1c/00000004
обрано 2:
   4b8a2f1c/00000001
   4b8a2f1c/00000002
```

Ідентифікатори потоків тут не наскрізні номери, а рядки, породжені з ідентифікатора вищого рівня, — вигляд у них залежить від контейнера, і покладатися на формат не можна: їх лише передають назад.

## Важелі поза елементом

Три речі змінюють вибір, не торкаючись жодного сигналу.

**Ранг фабрики.** Діє на весь процес, тож ставити його треба після `gst_init()` і до побудови конвеєра.

```c
static void
set_rank (const gchar *factory, GstRank rank)
{
  GstPluginFeature *f = gst_registry_find_feature (gst_registry_get (),
      factory, GST_TYPE_ELEMENT_FACTORY);
  if (f == NULL)
    return;                      /* такої фабрики в системі немає */
  gst_plugin_feature_set_rank (f, rank);
  gst_object_unref (f);
}

/* прибрати програмний декодер з-під ніг апаратного */
set_rank ("avdec_h264", GST_RANK_NONE);
```

`GST_RANK_NONE` (0) — не «заборонено», а «автодобір не візьме»; назване на ім'я, воно так само працює.

**Змінна середовища `GST_PLUGIN_FEATURE_RANK`** (з 1.18) робить те саме ззовні, без перезбирання. Пари розділяє кома, ім'я від рангу — двокрапка; ранг пишуть числом або одним із `NONE`, `MARGINAL`, `SECONDARY`, `PRIMARY`, `MAX`.

```
GST_PLUGIN_FEATURE_RANK=vah264dec:MAX,avdec_h264:NONE gst-launch-1.0 \
  filesrc location=clip.mkv ! decodebin ! fakesink
```

Фічу, якої в реєстрі немає, пропускають мовчки — описка в імені виглядає точно так само, як «не подіяло».

**Властивості просто з рядка конвеєра.** Усе з першої таблиці задається в `gst-launch-1.0` без жодного коду, і це найшвидший спосіб перевірити здогад:

```
gst-launch-1.0 filesrc location=clip.mkv \
  ! decodebin force-sw-decoders=true expose-all-streams=false \
              caps="video/x-h264" \
  ! fakesink
```

## Брак кодека: як прочитати повідомлення

Коли ланцюг обірвався, `decodebin` **спершу** постить на шину повідомлення `GST_MESSAGE_ELEMENT` спеціального вигляду й лише потім видає `unknown-type`. Розбирає таке повідомлення бібліотека pbutils:

```c
gboolean gst_is_missing_plugin_message                (GstMessage *msg);
/* обидва — transfer full, звільняти через g_free() */
gchar *  gst_missing_plugin_message_get_description   (GstMessage *msg);
gchar *  gst_missing_plugin_message_get_installer_detail (GstMessage *msg);

/* створити таке саме повідомлення самому — знадобиться у власному елементі */
GstMessage *gst_missing_decoder_message_new    (GstElement *element,
                                                const GstCaps *decode_caps);
GstMessage *gst_missing_encoder_message_new    (GstElement *element,
                                                const GstCaps *encode_caps);
GstMessage *gst_missing_element_message_new    (GstElement *element,
                                                const gchar *factory_name);
GstMessage *gst_missing_uri_source_message_new (GstElement *element,
                                                const gchar *protocol);
GstMessage *gst_missing_uri_sink_message_new   (GstElement *element,
                                                const gchar *protocol);
```

Два рядки, які повертає розбір, мають різне призначення, і плутати їх не можна.

| функція | що повертає | для чого |
|---|---|---|
| `…_get_description` | людський опис: `H.265 decoder` | показати користувачеві |
| `…_get_installer_detail` | непрозорий рядок | передати зовнішньому встановлювачу; **розбирати його не можна** |

```c
if (gst_is_missing_plugin_message (msg)) {
  gchar *what = gst_missing_plugin_message_get_description (msg);
  g_printerr ("бракує: %s\n", what);
  g_free (what);
}
```

Другий рядок віддають системному встановлювачу пакунків, якщо він у системі є:

```c
gboolean gst_install_plugins_supported                (void);
gboolean gst_install_plugins_installation_in_progress (void);
GstInstallPluginsReturn gst_install_plugins_sync  (const gchar * const *details,
                                                   GstInstallPluginsContext *ctx);
GstInstallPluginsReturn gst_install_plugins_async (const gchar * const *details,
                                                   GstInstallPluginsContext *ctx,
                                                   GstInstallPluginsResultFunc func,
                                                   gpointer user_data);
const gchar *gst_install_plugins_return_get_name  (GstInstallPluginsReturn ret);
```

| стала | значення | що сталося |
|---|---|---|
| `GST_INSTALL_PLUGINS_SUCCESS` | 0 | усе замовлене встановлено |
| `GST_INSTALL_PLUGINS_NOT_FOUND` | 1 | кандидатів на встановлення не знайшлося |
| `GST_INSTALL_PLUGINS_ERROR` | 2 | помилка встановлення |
| `GST_INSTALL_PLUGINS_PARTIAL_SUCCESS` | 3 | встановлено частину |
| `GST_INSTALL_PLUGINS_USER_ABORT` | 4 | користувач відмовився |
| `GST_INSTALL_PLUGINS_CRASHED` | 100 | встановлювач упав |
| `GST_INSTALL_PLUGINS_INVALID` | 101 | встановлювач повернув що-небудь незрозуміле |
| `GST_INSTALL_PLUGINS_STARTED_OK` | 200 | асинхронне встановлення розпочато |
| `GST_INSTALL_PLUGINS_INTERNAL_FAILURE` | 201 | внутрішня халепа під час запуску |
| `GST_INSTALL_PLUGINS_HELPER_MISSING` | 202 | допоміжної програми немає в системі |
| `GST_INSTALL_PLUGINS_INSTALL_IN_PROGRESS` | 203 | встановлення вже триває |

Після успішного встановлення реєстр треба перечитати — інакше процес далі житиме зі старим переліком фабрик і поводитиметься так, наче нічого не змінилося.

> [Підрахунок посилань](topic:programming/reference-counting) — лічильник живих власників усередині самого об'єкта. Саме тому кожен підпис тут має позначку `transfer none` або `transfer full`: перша означає «дали подивитися», друга — «посилання ваше, зніміть його самі».
