# 📋 API падів GStreamer 1.x: перелічення, сигнатури, володіння

Це настільна довідка по публічному API падів у GStreamer 1.x — усі перелічення з числовими значеннями, сигнатури функцій так, як вони записані в заголовках `gst/gstpad.h`, `gst/gstpadtemplate.h`, `gst/gstelement.h`, `gst/gstutils.h`, `gst/gstghostpad.h`, і окремо правила володіння посиланнями. Останнє тут не додаток, а половина справи: код із переплутаним володінням компілюється без єдиного попередження, працює хвилину й тече, доки не з'їсть пам'ять.

Числа в переліченнях варто читати уважно — у GStreamer вони підібрані так, щоб перевірка зводилася до порівняння з нулем, і код, який це знає, коротший за код, який перебирає члени.

## Три перелічення, що описують сам пад

| Перелічення | Член | Знач. | Що означає |
| --- | --- | --- | --- |
| `GstPadDirection` | `GST_PAD_UNKNOWN` | 0 | напрямок не заданий |
| *(gstpad.h)* | `GST_PAD_SRC` | 1 | пад віддає дані **з** елемента |
| | `GST_PAD_SINK` | 2 | пад приймає дані **в** елемент |
| `GstPadPresence` | `GST_PAD_ALWAYS` | 0 | пад є з моменту створення елемента |
| *(gstpadtemplate.h)* | `GST_PAD_SOMETIMES` | 1 | з'явиться під час роботи — або ніколи |
| | `GST_PAD_REQUEST` | 2 | створюється на замовлення |
| `GstPadMode` | `GST_PAD_MODE_NONE` | 0 | пад не активований, дані не рухаються |
| *(gstpad.h)* | `GST_PAD_MODE_PUSH` | 1 | верхній елемент штовхає буфери вниз |
| | `GST_PAD_MODE_PULL` | 2 | нижній елемент тягне дані запитами |

Три перелічення живуть на трьох різних рівнях, і плутанина між ними — джерело половини питань новачка. **Напрямок** належить самому падові й незмінний. **Спосіб появи** належить не падові, а його шаблонові — у самому екземплярі пада цього поля немає, бо існуючий пад уже існує, і питання «коли він з'явиться» для нього беззмістовне. **Режим** не належить нікому й задається під час активації падів, коли конвеєр переходить у `READY` і далі ([стани конвеєра](book:media-vision/states-lifecycle)) — тому `gst_pad_get_mode()` до запуску чесно поверне `GST_PAD_MODE_NONE`.

Шаблон збирають із перших двох плюс caps:

```c
GstPadTemplate *gst_pad_template_new (const gchar     *name_template,
                                      GstPadDirection  direction,
                                      GstPadPresence   presence,
                                      GstCaps         *caps);

/* статичний варіант — у структурі класу елемента */
#define GST_STATIC_PAD_TEMPLATE(padname, dir, pres, caps) { padname, dir, pres, caps }
```

У `name_template` для request-падів пишуть зразок із форматним полем — `"src_%u"`, `"sink_%u"`, `"src_%d"`, — і саме за цим зразком потім просять новий пад на ім'я.

## GstPadLinkReturn: сім кодів

```c
typedef enum {
  GST_PAD_LINK_OK               =  0,
  GST_PAD_LINK_WRONG_HIERARCHY  = -1,
  GST_PAD_LINK_WAS_LINKED       = -2,
  GST_PAD_LINK_WRONG_DIRECTION  = -3,
  GST_PAD_LINK_NOFORMAT         = -4,
  GST_PAD_LINK_NOSCHED          = -5,
  GST_PAD_LINK_REFUSED          = -6
} GstPadLinkReturn;
```

| Код | Знач. | Через що виникає | Що робити |
| --- | --- | --- | --- |
| `GST_PAD_LINK_OK` | 0 | з'єднання встановлено | — |
| `GST_PAD_LINK_WRONG_HIERARCHY` | −1 | у падів немає спільного предка | додати обидва елементи в один бін **до** з'єднання |
| `GST_PAD_LINK_WAS_LINKED` | −2 | один із падів уже має партнера | пад тримає рівно одного; роздавати потік — через `tee` |
| `GST_PAD_LINK_WRONG_DIRECTION` | −3 | src↔src, sink↔sink або переставлені аргументи | перший аргумент — завжди src |
| `GST_PAD_LINK_NOFORMAT` | −4 | перетин caps порожній | вставити перетворювач або звузити фільтр |
| `GST_PAD_LINK_NOSCHED` | −5 | не знайшлося спільного режиму роботи | один уміє лише pull, другий лише push |
| `GST_PAD_LINK_REFUSED` | −6 | власна link-функція пада сказала «ні» | причину знає елемент; дивитися його журнал |

Найчастіший на практиці — `−1`, і майже завжди він означає забутий `gst_bin_add()`: елементи створені, але ще нікому не належать, тож спільного предка в них немає. Другий за частотою — `−2` у сценарії «хочу той самий потік у двох місцях».

Знаки в цьому переліченні — інтерфейс, а не оформлення. На них тримаються два макроси й функція імені:

```c
#define GST_PAD_LINK_FAILED(ret)      ((ret) < GST_PAD_LINK_OK)
#define GST_PAD_LINK_SUCCESSFUL(ret)  ((ret) >= GST_PAD_LINK_OK)

const gchar *gst_pad_link_get_name (GstPadLinkReturn ret);
```

`gst_pad_link_get_name()` віддає готовий рядок назви коду — саме те, що варто друкувати в діагностиці замість числа.

## GstPadLinkCheck: скільки перевіряти перед з'єднанням

```c
typedef enum {
  GST_PAD_LINK_CHECK_NOTHING        = 0,
  GST_PAD_LINK_CHECK_HIERARCHY      = 1 << 0,   /* 0x1 */
  GST_PAD_LINK_CHECK_TEMPLATE_CAPS  = 1 << 1,   /* 0x2 */
  GST_PAD_LINK_CHECK_CAPS           = 1 << 2,   /* 0x4 */
  GST_PAD_LINK_CHECK_NO_RECONFIGURE = 1 << 3,   /* 0x8 */
  GST_PAD_LINK_CHECK_DEFAULT        = GST_PAD_LINK_CHECK_HIERARCHY |
                                      GST_PAD_LINK_CHECK_CAPS      /* 0x5 */
} GstPadLinkCheck;
```

| Прапорець | Що перевіряє | Ціна |
| --- | --- | --- |
| `NOTHING` | нічого | нуль — і вся відповідальність на вас |
| `HIERARCHY` | спільні предки падів | дешево; можна пропустити, коли точно знаєте, що елементи в одному біні |
| `TEMPLATE_CAPS` | сумісність за **шаблонними** caps | набагато дешевше за `CAPS` |
| `CAPS` | сумісність за відповіддю `gst_pad_query_caps()` | дорого: обидва пади опитують сусідів |
| `NO_RECONFIGURE` | *(не перевірка)* — не слати `reconfigure` вгору після з'єднання | — |
| `DEFAULT` | `HIERARCHY \| CAPS` — те, що робить звичайний `gst_pad_link()` | — |

Дві тонкощі, обидві прямо з заголовка. Перша: `CAPS` і `TEMPLATE_CAPS` **взаємовиключні**, і якщо вказати обидва, виконається дорожча й безпечніша перевірка `CAPS` — комбінація не дає «швидко й надійно». Друга: `TEMPLATE_CAPS` не просто швидша, а й **менш надійна** — шаблон, який оголошує `GST_CAPS_ANY`, пройде перевірку з будь-ким, а справжня несумісність вилізе згодом, уже під час [узгодження caps](book:media-vision/caps-negotiation), тобто на переході в `PAUSED` і у вигляді помилки на шині, а не коду повернення в рядку з'єднання.

Звідси правило, яке автори GStreamer записали в заголовку майже дослівно: послаблювати перевірки варто лише тоді, коли ви на сто відсотків певні, що з'єднання не може провалитися. Сумніваєтеся — беріть `DEFAULT`.

## З'єднання й розрив на рівні падів

```c
GstPadLinkReturn  gst_pad_link       (GstPad *srcpad, GstPad *sinkpad);
GstPadLinkReturn  gst_pad_link_full  (GstPad *srcpad, GstPad *sinkpad,
                                      GstPadLinkCheck flags);
gboolean          gst_pad_unlink     (GstPad *srcpad, GstPad *sinkpad);
gboolean          gst_pad_can_link   (GstPad *srcpad, GstPad *sinkpad);
gboolean          gst_pad_is_linked  (GstPad *pad);
GstPad           *gst_pad_get_peer   (GstPad *pad);
gboolean          gst_pad_set_active (GstPad *pad, gboolean active);
```

Порядок аргументів усюди однаковий і не має винятків: **спершу src, потім sink**. `gst_pad_link(a, b)` — це `gst_pad_link_full(a, b, GST_PAD_LINK_CHECK_DEFAULT)`.

`gst_pad_unlink()` повертає `gboolean`, а не код: або пади справді були з'єднані саме між собою і зв'язок знято, або ні. Розривати зв'язок у працюючому конвеєрі без блокувальної проби не можна — у цю мить у chain-функції нижнього елемента цілком може виконуватися чужий потік.

`gst_pad_get_peer()` повертає партнера **з підвищеним лічильником посилань** — це перше місце, де новачок залишає витік.

## Звідки беруться пади в елемента

```c
GstPad *gst_element_get_static_pad     (GstElement *element, const gchar *name);
GstPad *gst_element_request_pad_simple (GstElement *element, const gchar *name);
GstPad *gst_element_request_pad        (GstElement *element, GstPadTemplate *templ,
                                        const gchar *name, const GstCaps *caps);
void    gst_element_release_request_pad(GstElement *element, GstPad *pad);

GstIterator *gst_element_iterate_pads      (GstElement *element);
GstIterator *gst_element_iterate_src_pads  (GstElement *element);
GstIterator *gst_element_iterate_sink_pads (GstElement *element);
```

Вибір функції диктує саме `GstPadPresence`, і кожному способу появи відповідає рівно один спосіб дістати пад:

| Presence | Як дістати | Коли |
| --- | --- | --- |
| `ALWAYS` | `gst_element_get_static_pad(e, "src")` | одразу після `gst_element_factory_make()` |
| `SOMETIMES` | сигнал `"pad-added"` | ніяк не раніше, ніж елемент розбере вміст |
| `REQUEST` | `gst_element_request_pad_simple(e, "src_%u")` | коли ви самі вирішили, що потрібна ще одна гілка |

Ім'я в `request_pad_simple()` передають **зразком**, як у шаблоні, а не готовим числом: `"src_%u"` означає «дай наступний вільний». Явне `"src_3"` теж законне, коли номер важливий.

У версії **1.20** цю функцію додали як перейменування старої `gst_element_get_request_pad()` — сенс і поведінка ті самі, змінилася лише назва, бо `get_` у ній вводило в оману: функція не «дістає», а **створює** пад. Стара досі є, але позначена в заголовку атрибутом `G_DEPRECATED_FOR(gst_element_request_pad_simple)`, тож на свіжій збірці дає попередження компілятора. Для сумісності зі старішими рантаймами її ще можна побачити під `#if GST_CHECK_VERSION(1,20,0)`.

Повний `gst_element_request_pad()` відрізняється тим, що бере шаблон і бажані caps — це шлях для елементів на кшталт `input-selector`, які вибирають між кількома шаблонами request-падів.

## Обгортки рівня елементів

```c
gboolean gst_element_link               (GstElement *src, GstElement *dest);
gboolean gst_element_link_many          (GstElement *e1, GstElement *e2, ...);  /* NULL-термінований */
gboolean gst_element_link_filtered      (GstElement *src, GstElement *dest,
                                         GstCaps *filter);
gboolean gst_element_link_pads          (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname);
gboolean gst_element_link_pads_full     (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname,
                                         GstPadLinkCheck flags);
gboolean gst_element_link_pads_filtered (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname,
                                         GstCaps *filter);
void     gst_element_unlink             (GstElement *src, GstElement *dest);
void     gst_element_unlink_many        (GstElement *e1, GstElement *e2, ...);
void     gst_element_unlink_pads        (GstElement *src, const gchar *srcpadname,
                                         GstElement *dest, const gchar *destpadname);
```

Усе це — надбудова над `gst_pad_link()`, яка сама шукає придатну пару падів. `NULL` замість імені пада означає «будь-який відповідний». Три властивості цих обгорток варто знати напам'ять.

**Вони повертають `gboolean`, а не код.** Причина невдачі губиться: `FALSE` однаково означає і забутий `gst_bin_add()`, і несумісні формати, і відсутність падів. Тому в діагностиці незрозумілої невдачі перший крок — переписати саме цю ланку на явні `gst_element_get_static_pad()` + `gst_pad_link()` і надрукувати `gst_pad_link_get_name()`.

**Вони можуть створювати request-пади.** Це прямо записано в документації: функція шукає вільні наявні пади, а за потреби **замовляє нові** — і такі пади потім треба звільняти вручну через `gst_element_release_request_pad()`. Через це `gst_element_link(tee, queue)` виглядає невинно, але залишає за собою замовлений пад, про який ніхто більше не пам'ятає.

**Фільтр не передає володіння.** У `*_filtered` параметр `filter` анотований як `transfer none`: caps лишаються вашими, і `gst_caps_unref()` після виклику — ваш обов'язок. Це протилежність поведінки `gst_pad_push()`, і саме тому обидва випадки зібрані нижче в одну таблицю.

## Рух даних і GstFlowReturn

```c
GstFlowReturn gst_pad_push       (GstPad *pad, GstBuffer *buffer);
GstFlowReturn gst_pad_push_list  (GstPad *pad, GstBufferList *list);
gboolean      gst_pad_push_event (GstPad *pad, GstEvent *event);
GstFlowReturn gst_pad_pull_range (GstPad *pad, guint64 offset, guint size,
                                  GstBuffer **buffer);
gboolean      gst_pad_peer_query (GstPad *pad, GstQuery *query);
gboolean      gst_pad_query      (GstPad *pad, GstQuery *query);
```

`gst_pad_pull_range()` кличуть **на sink-паді**, активованому в режимі `PULL`; `offset` рахують у байтах від початку, а `*buffer` повертається новим посиланням. `gst_pad_peer_query()` виконує запит на паді-партнері; структуру запиту створюєте й звільняєте ви самі — володіння не передається.

```c
typedef enum {
  GST_FLOW_CUSTOM_SUCCESS_2 =  102,
  GST_FLOW_CUSTOM_SUCCESS_1 =  101,
  GST_FLOW_CUSTOM_SUCCESS   =  100,
  GST_FLOW_OK               =    0,
  GST_FLOW_NOT_LINKED       =   -1,
  GST_FLOW_FLUSHING         =   -2,
  GST_FLOW_EOS              =   -3,
  GST_FLOW_NOT_NEGOTIATED   =   -4,
  GST_FLOW_ERROR            =   -5,
  GST_FLOW_NOT_SUPPORTED    =   -6,
  GST_FLOW_CUSTOM_ERROR     = -100,
  GST_FLOW_CUSTOM_ERROR_1   = -101,
  GST_FLOW_CUSTOM_ERROR_2   = -102
} GstFlowReturn;

const gchar *gst_flow_get_name (GstFlowReturn ret);
```

| Код | Знач. | Що сталося | Реакція |
| --- | --- | --- | --- |
| `GST_FLOW_OK` | 0 | дані прийнято | штовхати далі |
| `GST_FLOW_NOT_LINKED` | −1 | у пада немає партнера | джерело зупиняє свій потік — **не помилка** |
| `GST_FLOW_FLUSHING` | −2 | пад скидає дані або деактивований | негайно вийти, нічого не робити з буфером |
| `GST_FLOW_EOS` | −3 | нижче даних більше не чекають | завершити подачу |
| `GST_FLOW_NOT_NEGOTIATED` | −4 | буфер прийшов, а формат не погоджений | помилка узгодження |
| `GST_FLOW_ERROR` | −5 | справжня помилка | подробиці елемент **зобов'язаний** надіслати окремим `GST_MESSAGE_ERROR` на шину |
| `GST_FLOW_NOT_SUPPORTED` | −6 | операція не підтримується | напр. `pull_range` на паді, що вміє лише push |
| `GST_FLOW_CUSTOM_*` | ±100…102 | приватні коди елемента | ядро їх не тлумачить, лише передає далі |

Знак і тут несе сенс: усе, що ≥ 0, — успіх, усе, що < 0, — ні. А всередині від'ємних заголовок проводить власну межу, яку легко проґавити: `NOT_LINKED` і `FLUSHING` позначені там як **очікувані** невдачі, решта — як помилки. Практичний наслідок прямий: отримавши `−1` чи `−2`, елемент **не повинен** сипати повідомленням про помилку на шину. Гілку від'єднали або конвеєр перемотують — це штатний хід подій, і єдина правильна реакція — тихо припинити роботу.

`GST_FLOW_ERROR`, навпаки, сам собою не несе жодної інформації для користувача: число −5 не скаже, що саме не відкрилося. Тому за домовленістю елемент спершу шле `GST_MESSAGE_ERROR` із доменом, кодом і текстом, а вже тоді повертає −5.

## Caps і запити на паді

```c
GstCaps *gst_pad_get_current_caps      (GstPad *pad);
GstCaps *gst_pad_query_caps            (GstPad *pad, GstCaps *filter);
GstCaps *gst_pad_peer_query_caps       (GstPad *pad, GstCaps *filter);
GstCaps *gst_pad_get_allowed_caps      (GstPad *pad);
GstCaps *gst_pad_get_pad_template_caps (GstPad *pad);
```

Чотири функції звучать схоже, а відповідають на чотири різні питання — і взяти не ту означає побачити не те:

| Виклик | Відповідає на питання | Коли має сенс |
| --- | --- | --- |
| `get_current_caps` | «який формат **зараз** тече» | лише після узгодження; до `PAUSED` віддасть `NULL` |
| `get_pad_template_caps` | «що пад уміє **в принципі**» | будь-коли, навіть до запуску |
| `query_caps` | «що пад готовий прийняти **зараз**, з урахуванням сусідів» | під час узгодження |
| `get_allowed_caps` | «що влаштує **обох** — пад і його партнера» | після з'єднання, до узгодження |

`filter` у запитах — необов'язкове звуження: передали `NULL` — отримали все, передали конкретні caps — отримали перетин. Володіння фільтром не переходить, а от результат кожної з п'яти функцій — нове посилання, яке треба звільнити `gst_caps_unref()`.

## Проби: типи, коди, структура

```c
gulong gst_pad_add_probe    (GstPad *pad, GstPadProbeType mask,
                             GstPadProbeCallback callback,
                             gpointer user_data, GDestroyNotify destroy_data);
void   gst_pad_remove_probe (GstPad *pad, gulong id);

typedef GstPadProbeReturn (*GstPadProbeCallback) (GstPad *pad,
                                                  GstPadProbeInfo *info,
                                                  gpointer user_data);
```

Маска — прапорці, тож типи комбінують через `|`:

| Прапорець `GST_PAD_PROBE_TYPE_…` | Біт | Hex | Ловить |
| --- | --- | --- | --- |
| `IDLE` | `1 << 0` | 0x0001 | мить, коли через пад нічого не проходить |
| `BLOCK` | `1 << 1` | 0x0002 | перший елемент даних — і тримає його |
| `BUFFER` | `1 << 4` | 0x0010 | буфер |
| `BUFFER_LIST` | `1 << 5` | 0x0020 | список буферів |
| `EVENT_DOWNSTREAM` | `1 << 6` | 0x0040 | подію вниз за потоком |
| `EVENT_UPSTREAM` | `1 << 7` | 0x0080 | подію вгору проти потоку |
| `EVENT_FLUSH` | `1 << 8` | 0x0100 | подію скидання |
| `QUERY_DOWNSTREAM` | `1 << 9` | 0x0200 | запит вниз |
| `QUERY_UPSTREAM` | `1 << 10` | 0x0400 | запит угору |
| `PUSH` | `1 << 12` | 0x1000 | лише коли пад працює в push |
| `PULL` | `1 << 13` | 0x2000 | лише коли пад працює в pull |

Готові комбінації з заголовка — щоб не збирати руками:

```
BLOCKING          = IDLE | BLOCK                                    0x0003
DATA_DOWNSTREAM   = BUFFER | BUFFER_LIST | EVENT_DOWNSTREAM         0x0070
DATA_UPSTREAM     = EVENT_UPSTREAM                                  0x0080
DATA_BOTH         = DATA_DOWNSTREAM | DATA_UPSTREAM                 0x00F0
BLOCK_DOWNSTREAM  = BLOCK | DATA_DOWNSTREAM                         0x0072
BLOCK_UPSTREAM    = BLOCK | DATA_UPSTREAM                           0x0082
EVENT_BOTH        = EVENT_DOWNSTREAM | EVENT_UPSTREAM               0x00C0
QUERY_BOTH        = QUERY_DOWNSTREAM | QUERY_UPSTREAM               0x0600
ALL_BOTH          = DATA_BOTH | QUERY_BOTH                          0x06F0
SCHEDULING        = PUSH | PULL                                     0x3000
```

Одна пастка видна прямо з цих формул: **`EVENT_FLUSH` не входить у `DATA_DOWNSTREAM`** — і взагалі в жодну комбінацію. Проба з маскою `DATA_BOTH` побачить буфери, caps, segment, EOS — і не побачить `flush-start`/`flush-stop`. Хочете ловити перемотування — додавайте `GST_PAD_PROBE_TYPE_EVENT_FLUSH` окремо.

Коди повернення проби:

| Код | Знач. | Наслідок |
| --- | --- | --- |
| `GST_PAD_PROBE_DROP` | 0 | елемент даних далі не йде; інші проби на нього вже не кличуть; той, хто штовхав, отримує `GST_FLOW_OK` — тобто **успіх**, дані просто зникли |
| `GST_PAD_PROBE_OK` | 1 | звичайна відповідь: проба лишається, рішення віддано іншим пробам; якщо їх немає — типова поведінка типу проби (блокувальна блокує, звичайна пропускає) |
| `GST_PAD_PROBE_REMOVE` | 2 | пропустити дані й **зняти цю пробу**; для блокувальної це і є спосіб розблокувати потік |
| `GST_PAD_PROBE_PASS` | 3 | пропустити цей елемент і заблокуватися на наступному; якщо хоч одна проба з кількох повернула `PASS` — дані підуть |
| `GST_PAD_PROBE_HANDLED` | 4 | «я все зробив сам, далі не передавати» |

`DROP` і `HANDLED` дають зовні однаковий ефект — дані не йдуть далі, — але розходяться в тому, хто прибирає. При `DROP` буфер чи подію звільняє GStreamer. При `HANDLED` **звільняєте ви**: пропустите `gst_buffer_unref()` — отримаєте витік на кожному кадрі. Натомість `HANDLED` дозволяє те, чого не може `DROP`: підмінити код, який побачить верхній елемент, — макросом `GST_PAD_PROBE_INFO_FLOW_RETURN(info)` (з'явилося в 1.6). Так проба вміє, наприклад, повернути `GST_FLOW_EOS` угору, не чіпаючи жодного елемента.

Дані витягають із `GstPadProbeInfo`:

```c
struct _GstPadProbeInfo {
  GstPadProbeType type;
  gulong          id;
  gpointer        data;
  guint64         offset;
  guint           size;
};

#define GST_PAD_PROBE_INFO_TYPE(d)        ((d)->type)
#define GST_PAD_PROBE_INFO_ID(d)          ((d)->id)
#define GST_PAD_PROBE_INFO_DATA(d)        ((d)->data)
#define GST_PAD_PROBE_INFO_FLOW_RETURN(d) ((d)->ABI.abi.flow_ret)

GstBuffer     *gst_pad_probe_info_get_buffer      (GstPadProbeInfo *info);
GstBufferList *gst_pad_probe_info_get_buffer_list (GstPadProbeInfo *info);
GstEvent      *gst_pad_probe_info_get_event       (GstPadProbeInfo *info);
GstQuery      *gst_pad_probe_info_get_query       (GstPadProbeInfo *info);
```

Функції-акцесори кращі за прямий `info->data` тим, що самі перевіряють `type` і повертають `NULL`, коли зараз іде не той тип даних. Одна маска легко ловить і буфери, і події — без перевірки код розіб'ється на першій же події `caps`, розтлумаченій як буфер.

Два зауваження про сам `gst_pad_add_probe()`. По-перше, `IDLE`-проба може виконатися **синхронно, просто всередині виклику**, у тому ж потоці, — якщо пад саме зараз простоює. По-друге, як наслідок: якщо така негайно виконана проба повернула `REMOVE`, функція віддасть `0`, і це не помилка, а нормальний результат «уже спрацювало й уже знято». Порядок виклику груп теж зафіксований: спершу `BLOCK`-проби, потім усі інші, наостанок `IDLE`.

## Привидні пади

```c
GstPad *gst_ghost_pad_new                        (const gchar *name, GstPad *target);
GstPad *gst_ghost_pad_new_no_target              (const gchar *name, GstPadDirection dir);
GstPad *gst_ghost_pad_new_from_template          (const gchar *name, GstPad *target,
                                                  GstPadTemplate *templ);
GstPad *gst_ghost_pad_new_no_target_from_template(const gchar *name, GstPadTemplate *templ);
GstPad *gst_ghost_pad_get_target                 (GstGhostPad *gpad);
gboolean gst_ghost_pad_set_target                (GstGhostPad *gpad, GstPad *newtarget);
```

Варіанти `no_target` існують саме для sometimes-падів: коли бін уже треба вставити в конвеєр, а внутрішнього пада, на який привид указуватиме, ще немає. Тоді пад створюють без цілі — звідси й обов'язковий явний `GstPadDirection`, бо взяти напрямок нема звідки, — а `gst_ghost_pad_set_target()` кличуть згодом, коли ціль з'явиться. Передане в `set_target()` значення `NULL` законне й відчіплює привида від цілі.

Готовий привидний пад додають до біна звичайним `gst_element_add_pad(GST_ELEMENT(bin), ghost)`, після чого бін ззовні нічим не відрізняється від звичайного елемента.

## Хто володіє посиланням

![Три рядки: виклик ліворуч, стрілка з підписом, наслідок для посилання праворуч](/reference/media-vision/gstreamer/pads-and-linking/img/pad-ownership.svg)

*Три режими володіння: віддали, отримали, позичили. Переплутати їх коштує або витоку, або подвійного звільнення — а компілятор не скаже нічого.*

| Виклик | Що з посиланням | Ваш обов'язок |
| --- | --- | --- |
| `gst_pad_push(pad, buf)` | буфер **переходить** до GStreamer | нічого; після виклику `buf` чіпати не можна — **навіть якщо повернулася помилка** |
| `gst_pad_push_list(pad, list)` | те саме зі списком | нічого |
| `gst_pad_push_event(pad, ev)` | подія **переходить** | треба лишити собі — `gst_event_ref()` **до** виклику |
| `gst_pad_pull_range(…, &buf)` | ви отримали **нове** посилання | `gst_buffer_unref(buf)` |
| `gst_element_get_static_pad()` | +1 посилання | `gst_object_unref(pad)` |
| `gst_pad_get_peer()` | +1 посилання | `gst_object_unref(peer)` |
| `gst_ghost_pad_get_target()` | +1 посилання | `gst_object_unref(target)` |
| `gst_element_request_pad_simple()` | +1 **і створено пад** | спершу `gst_element_release_request_pad()`, **потім** `gst_object_unref()` |
| `gst_pad_get_current_caps()` та решта caps-функцій | +1 посилання на caps | `gst_caps_unref(caps)` |
| `gst_element_link_filtered(…, filter)` | `transfer none` — caps лишаються вашими | `gst_caps_unref(filter)` |
| `gst_pad_peer_query(pad, q)` | запит лишається вашим | `gst_query_unref(q)` |
| `GST_PAD_PROBE_INFO_DATA(info)` | **позичене** на час виклику | не звільняти; треба довше — `gst_buffer_ref()` |

Найпідступніший рядок — перший. `gst_pad_push()` забирає посилання **завжди**, включно з випадком, коли повернула `GST_FLOW_ERROR`. Природний рефлекс «не вийшло — приберу за собою» тут дає подвійне звільнення й падіння в геть іншому місці програми, за десятки кадрів по тому. Симетрична пастка — рядок про request-пад: `release_request_pad()` каже елементові «пад більше не потрібен», але **не** знімає вашого власного посилання; потрібні обидва виклики й саме в такому порядку.

Тонкощі спільного володіння буферами між елементами — окрема механіка, і вона визначає, коли кадр копіюється, а коли ні ([буфери й пам'ять](book:media-vision/buffers-and-memory)).

## Мінімальний робочий виклик

Програма з'єднує перший стик руками, щоб бачити код помилки, другий — обгорткою, вішає пробу на буфери й акуратно все звільняє. Збірка:

```sh
gcc pads-min.c -o pads-min $(pkg-config --cflags --libs gstreamer-1.0)
```

```c
#include <gst/gst.h>

static GstPadProbeReturn
on_buffer (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  guint *n = user_data;
  GstBuffer *buf = gst_pad_probe_info_get_buffer (info);   /* позичене */

  if (buf != NULL) {
    (*n)++;
    g_print ("буфер %2u  pts %" GST_TIME_FORMAT "\n",
             *n, GST_TIME_ARGS (GST_BUFFER_PTS (buf)));
  }
  return GST_PAD_PROBE_OK;                  /* пропустити далі, пробу лишити */
}

int
main (int argc, char **argv)
{
  guint n = 0;

  gst_init (&argc, &argv);

  GstElement *pipe = gst_pipeline_new ("p");
  GstElement *src  = gst_element_factory_make ("videotestsrc", NULL);
  GstElement *conv = gst_element_factory_make ("videoconvert", NULL);
  GstElement *sink = gst_element_factory_make ("fakesink", NULL);

  g_object_set (src, "num-buffers", 10, NULL);

  /* спершу в бін — інакше буде GST_PAD_LINK_WRONG_HIERARCHY */
  gst_bin_add_many (GST_BIN (pipe), src, conv, sink, NULL);

  GstPad *srcpad  = gst_element_get_static_pad (src,  "src");    /* +1 */
  GstPad *sinkpad = gst_element_get_static_pad (conv, "sink");   /* +1 */

  GstPadLinkReturn lr = gst_pad_link (srcpad, sinkpad);
  if (GST_PAD_LINK_FAILED (lr)) {
    g_printerr ("не з'єдналося: %s\n", gst_pad_link_get_name (lr));
    return 1;
  }
  gst_object_unref (sinkpad);            /* більше не потрібен — віддаємо */

  /* обгортка: зручно, але причини невдачі не скаже */
  if (!gst_element_link (conv, sink))
    g_printerr ("videoconvert ! fakesink: не з'єдналося\n");

  gulong probe_id = gst_pad_add_probe (srcpad, GST_PAD_PROBE_TYPE_BUFFER,
                                       on_buffer, &n, NULL);

  gst_element_set_state (pipe, GST_STATE_PLAYING);

  GstBus *bus = gst_element_get_bus (pipe);
  GstMessage *msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE,
      GST_MESSAGE_EOS | GST_MESSAGE_ERROR);

  if (msg != NULL && GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ERROR) {
    GError *err = NULL;
    gst_message_parse_error (msg, &err, NULL);
    g_printerr ("помилка: %s\n", err->message);
    g_clear_error (&err);
  }

  gst_pad_remove_probe (srcpad, probe_id);
  gst_element_set_state (pipe, GST_STATE_NULL);

  if (msg != NULL)
    gst_message_unref (msg);
  gst_object_unref (bus);
  gst_object_unref (srcpad);             /* наше посилання з get_static_pad */
  gst_object_unref (pipe);
  return 0;
}
```

Окремо — повний цикл request-пада, бо він єдиний вимагає двох різних звільнень:

```c
GstPad *tee_src = gst_element_request_pad_simple (tee, "src_%u");  /* створено, +1 */
GstPad *q_sink  = gst_element_get_static_pad (queue, "sink");      /* +1 */

if (GST_PAD_LINK_FAILED (gst_pad_link (tee_src, q_sink)))
  g_printerr ("гілка tee не під'єдналася\n");

/* … робота … */

gst_pad_unlink (tee_src, q_sink);
gst_object_unref (q_sink);                       /* посилання з get_static_pad */

gst_element_release_request_pad (tee, tee_src);  /* 1) сказати елементу */
gst_object_unref (tee_src);                      /* 2) віддати своє посилання */
```
