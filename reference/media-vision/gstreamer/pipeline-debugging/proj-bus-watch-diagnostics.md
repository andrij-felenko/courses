# ⚙️ Спостерігач шини, що сам збирає докази

Це діагностична обв'язка на двісті рядків, яку прикручують до готового конвеєра одним викликом і більше про неї не згадують: доки все гаразд, вона мовчить, а коли ламається — сама друкує обидві половини помилки, сама скидає граф конвеєра на диск **у мілісекунду аварії** й сама доповідає, у якому саме стані все застрягло, якщо `PLAYING` так і не настав.

Потреба в ній береться з простої арифметики часу. Несправність у конвеєрі триває мить: елемент постить `ERROR`, конвеєр згортається, і вже за секунду в пам'яті немає ні того графа, ні тих узгоджених форматів, ні тих станів, які могли б пояснити, що сталося. Людина за терміналом цієї втрати не помічає — вона просто перезапускає з `GST_DEBUG=4` і дивиться ще раз. Пристрій, що місяць працює в полі, другого разу не дає: наступний збій буде через тиждень, і біля нього знову нікого не буде. Тому докази має збирати той, хто на місці події, — сама програма, тоді ж, коли подія відбувається.

## Задача

Обв'язка мусить робити п'ять речей.

**Друкувати помилку цілком.** Повідомлення `ERROR` несе дві частини: `GError` із текстом для людини й окремий зневаджувальний рядок, у якому записано файл із номером рядка, ім'я функції та повний шлях елемента в графі. Перша частина часто не означає нічого («Internal data stream error»), друга називає винного поіменно. Те саме стосується `WARNING` та `INFO` — вони влаштовані однаково й розбираються тією ж парою вказівників.

**Ловити брак плагіна.** Повідомлення про кодек, якого в системі не знайшлося, приходить **окремо й раніше** за помилку, іншим типом, і тільки в ньому написано, чого саме бракує. Програма, яка дивиться лише на `ERROR`, дізнається «не змогли декодувати» замість «немає декодера H.264».

**Скидати граф у момент аварії.** З часовою міткою в імені, щоб серія знімків не затирала сама себе.

**Стежити за годинником.** Якщо за `N` секунд конвеєр не доїхав до `PLAYING` — доповісти, де він стоїть. Це єдиний спосіб відрізнити «застряг у `PAUSED`» від «не вийшов із `READY`», а це два зовсім різні діагнози.

**Розбирати відповідь `set_state`.** Зокрема `NO_PREROLL`, яке не є помилкою й читається як «джерело живе».

І одну річ вона робити **не мусить**: вирішувати за програму, що робити далі. Не зупиняти цикл, не перебудовувати конвеєр, не глушити помилку. Обв'язка — свідок, а не суддя; логіка застосунку живе окремо й будується зовсім інакше — приклад такої логіки розібрано у [робочому циклі шини](book:media-vision/bus-and-messages/proj-bus-loop.md).

## Ідея: одна структура, два виклики

Усе, що обв'язці потрібно пам'ятати, — це вказівник на конвеєр, вказівник на його шину, два ідентифікатори джерел подій (стеження й таймер), префікс для імен файлів і два прапорці. Одна структура, один виклик на приєднання, один на від'єднання.

Ключове рішення тут — **де взяти стан у момент, коли конвеєр не відповідає**. Спокуса очевидна: спитати `gst_element_get_state()` і зачекати на відповідь. Саме так обв'язка й перетворюється на частину несправності — про це нижче окремо. Правильний хід протилежний: питати з **нульовою** витримкою, тобто «що є просто зараз, не чекаючи ні миті». Відповідь із нулем ніколи не блокує й повертає рівно те, що потрібно: поточний стан, стан у черзі та код переходу.

Друге рішення — **скидати граф не за розкладом, а за подією**. Граф, знятий раз на хвилину, майже завжди знімає здоровий конвеєр. Граф, знятий з обробника помилки, знімає той єдиний, який має значення.

## Код

### Каркас і приєднання

:::tabs
```c
/* gstdiag.c — діагностична обв'язка. Чіпляється до будь-якого конвеєра
   й мовчить, доки все добре. */

#include <gst/gst.h>
#include <gst/pbutils/pbutils.h>   /* розпізнавання повідомлень про брак плагіна */
#include <glib/gstdio.h>           /* g_mkdir_with_parents() */

typedef struct {
  GstElement *pipeline;
  GstBus     *bus;
  guint       watch_id;    /* джерело подій шини в головному циклі */
  guint       guard_id;    /* сторожовий таймер; 0 — знято */
  guint       guard_sec;   /* скільки секунд чекати на PLAYING */
  const gchar *tag;        /* префікс імен dot-файлів */
  gboolean    is_live;     /* джерело живе: прероллу не буде за визначенням */
  gint64      qos_last;    /* коли востаннє друкували QoS, монотонні мкс */
} Diag;

static gboolean diag_bus   (GstBus *bus, GstMessage *msg, gpointer data);
static gboolean diag_guard (gpointer data);

/* Повний шлях елемента в графі, як його друкує сам GStreamer:
   /GstPipeline:pipeline0/GstQTDemux:qtdemux0. Звільняє викликач. */
static gchar *src_path (GstMessage *msg)
{
  GstObject *src = GST_MESSAGE_SRC (msg);
  return src ? gst_object_get_path_string (src) : g_strdup ("(без джерела)");
}

/* Знімок графа з часовою міткою в імені. */
static void diag_dump (Diag *d, const gchar *why)
{
#ifdef GST_DISABLE_GST_DEBUG
  (void) d; (void) why;
  g_printerr ("  графа не буде: бібліотеку зібрано без діагностики\n");
#else
  gchar *name = g_strdup_printf ("%s-%s", d->tag, why);
  GST_DEBUG_BIN_TO_DOT_FILE_WITH_TS (GST_BIN (d->pipeline),
                                     GST_DEBUG_GRAPH_SHOW_ALL, name);
  g_printerr ("  граф скинуто: $GST_DEBUG_DUMP_DOT_DIR/<час>-%s.dot\n", name);
  g_free (name);
#endif
}

void diag_attach (Diag *d, GstElement *pipeline, const gchar *tag, guint guard_sec)
{
  d->pipeline  = gst_object_ref (pipeline);
  d->bus       = gst_element_get_bus (pipeline);
  d->tag       = tag;
  d->guard_sec = guard_sec;

  d->watch_id = gst_bus_add_watch (d->bus, diag_bus, d);
  if (d->watch_id == 0)
    g_printerr ("на шині вже висить чуже стеження — діагностика НЕ приєдналася\n");

  if (guard_sec > 0)
    d->guard_id = g_timeout_add_seconds (guard_sec, diag_guard, d);
}

void diag_detach (Diag *d)
{
  if (d->guard_id) { g_source_remove (d->guard_id);   d->guard_id = 0; }
  if (d->watch_id) { gst_bus_remove_watch (d->bus);   d->watch_id = 0; }
  if (d->bus)      { gst_object_unref (d->bus);       d->bus      = NULL; }
  if (d->pipeline) { gst_object_unref (d->pipeline);  d->pipeline = NULL; }
}
```
```py
"""gstdiag.py — діагностична обв'язка для будь-якого конвеєра."""
import sys
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstPbutils", "1.0")
from gi.repository import Gst, GstPbutils, GLib


class Diag:
    def __init__(self, pipeline, tag, guard_sec=10):
        self.pipeline = pipeline
        self.bus = pipeline.get_bus()
        self.tag = tag
        self.guard_sec = guard_sec
        self.is_live = False          # джерело живе: прероллу не буде за визначенням
        self.qos_last = 0             # коли востаннє друкували QoS, монотонні мкс

        self.watch_id = self.bus.add_watch(GLib.PRIORITY_DEFAULT, self._on_message, None)
        if self.watch_id == 0:
            print("на шині вже висить чуже стеження — діагностика НЕ приєдналася",
                  file=sys.stderr)

        self.guard_id = (GLib.timeout_add_seconds(guard_sec, self._guard)
                         if guard_sec else 0)

    @staticmethod
    def _src_path(msg):
        """Повний шлях елемента в графі: /GstPipeline:pipeline0/GstQTDemux:qtdemux0."""
        return msg.src.get_path_string() if msg.src else "(без джерела)"

    def _dump(self, why):
        """Знімок графа з часовою міткою в імені."""
        Gst.debug_bin_to_dot_file_with_ts(self.pipeline, Gst.DebugGraphDetails.ALL,
                                          f"{self.tag}-{why}")
        print(f"  граф скинуто: $GST_DEBUG_DUMP_DOT_DIR/<час>-{self.tag}-{why}.dot",
              file=sys.stderr)

    def detach(self):
        if self.guard_id:
            GLib.source_remove(self.guard_id)
            self.guard_id = 0
        if self.watch_id:
            self.bus.remove_watch()
            self.watch_id = 0
```
:::

Перевірка `watch_id == 0` варта того рядка, який вона займає. Шина тримає рівно **одне** стеження; другий виклик `gst_bus_add_watch()` нічого не приєднає й поверне нуль. Ситуація виникає сама собою, щойно обв'язку прикручують до конвеєра, у якому вже є свій обробник, — і без перевірки виглядає це як мовчазна діагностика, що чомусь не діагностує.

### Розбір помилки: друга половина важливіша за першу

`ERROR`, `WARNING` та `INFO` влаштовані однаково: усі три віддають пару «`GError` плюс зневаджувальний рядок» і різняться лише тим, що з ними робить програма. Тому розбір спільний, а рішення — назовні.

:::tabs
```c
/* Розбір ERROR / WARNING / INFO. Повідомлення позичене — НЕ звільняємо. */
static void diag_report (Diag *d, GstMessage *msg, const gchar *kind)
{
  GError *err = NULL;
  gchar  *dbg = NULL;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR:   gst_message_parse_error   (msg, &err, &dbg); break;
    case GST_MESSAGE_WARNING: gst_message_parse_warning (msg, &err, &dbg); break;
    default:                  gst_message_parse_info    (msg, &err, &dbg); break;
  }

  gchar *path = src_path (msg);
  g_printerr ("%s: %s\n", kind, err ? err->message : "(без тексту)");
  g_printerr ("  елемент: %s\n", path);
  if (err)
    g_printerr ("  домен:   %s, код %d\n", g_quark_to_string (err->domain), err->code);
  /* Ось заради чого все: файл, рядок, функція і шлях у графі. */
  g_printerr ("  місце:   %s\n", dbg ? dbg : "(бібліотека не дала подробиць)");

  g_free (path);
  g_clear_error (&err);   /* GError виділено ЗА НАС — власник ми */
  g_free (dbg);           /* рядок теж наш */
}
```
```py
    def _report(self, msg, kind):
        """Розбір ERROR / WARNING / INFO."""
        if msg.type == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
        elif msg.type == Gst.MessageType.WARNING:
            err, dbg = msg.parse_warning()
        else:
            err, dbg = msg.parse_info()

        print(f"{kind}: {err.message}", file=sys.stderr)
        print(f"  елемент: {self._src_path(msg)}", file=sys.stderr)
        print(f"  домен:   {err.domain}, код {err.code}", file=sys.stderr)
        # Ось заради чого все: файл, рядок, функція і шлях у графі.
        print(f"  місце:   {dbg or '(бібліотека не дала подробиць)'}", file=sys.stderr)
```
:::

Виглядає вивід так — і саме рядок «місце» перетворює безглузду фразу на адресу:

```
ПОМИЛКА: Internal data stream error.
  елемент: /GstPipeline:pipeline0/GstQTDemux:qtdemux0
  домен:   gst-stream-error-quark, код 1
  місце:   ../gst/isomp4/qtdemux.c(6073): gst_qtdemux_loop ():
           /GstPipeline:pipeline0/GstQTDemux:qtdemux0:
           streaming stopped, reason not-linked (-1)
  граф скинуто: $GST_DEBUG_DUMP_DOT_DIR/<час>-cam0-error.dot
```

> 🔧 **Навіщо це.** Перший рядок однаковий для доброї сотні різних несправностей — він каже лише «потік урвався». Останній рядок зневаджувальної частини називає **код зупинки потоку**, і саме він розводить причини: `not-linked (-1)` означає непід'єднаний пад, `not-negotiated (-4)` — порожній перетин форматів, `flushing (-2)` — конвеєр саме розчищають. Три різні механізми, три різні місця, де шукати, — і одна спільна фраза нагорі.

### Брак плагіна приходить окремо

Коли `decodebin` не знаходить декодера, він спершу постить повідомлення типу `ELEMENT` із докладним описом того, чого бракує, і аж потім — звичайну помилку. Перше повідомлення розпізнає й розбирає бібліотека `pbutils`; про те, звідки взагалі береться перелік доступних елементів, ідеться в темі про [модель плагінів](book:media-vision/plugin-model).

```c
    case GST_MESSAGE_ELEMENT:
      if (gst_is_missing_plugin_message (msg)) {
        gchar *desc = gst_missing_plugin_message_get_description (msg);
        gchar *inst = gst_missing_plugin_message_get_installer_detail (msg);
        g_printerr ("БРАКУЄ ПЛАГІНА: %s\n", desc ? desc : "(без опису)");
        g_printerr ("  рядок для встановлювача: %s\n", inst ? inst : "(немає)");
        g_free (desc);   /* обидві функції віддають щойно виділені рядки */
        g_free (inst);
        diag_dump (d, "missing-plugin");
      }
      break;
```

Опис читається людиною («H.264 decoder»), а другий рядок — це машинний ключ, за яким система вміє сама доставити потрібний пакунок. На робочому пристрої другий рядок цінніший: він однозначно ідентифікує брак, тоді як опис міняється від версії до версії.

### QoS: скільки кадрів уже викинуто

`QOS` — єдине повідомлення в цьому наборі, яке приходить **часто**. Стік, що не встигає, постить його на кожен викинутий кадр, тож друкувати все підряд означає утопити журнал. Тому тут стоїть загорожа за часом: не частіше ніж раз на секунду, зате з накопиченими лічильниками.

```c
    case GST_MESSAGE_QOS: {
      gint64 now = g_get_monotonic_time ();
      if (now - d->qos_last < G_USEC_PER_SEC)
        break;                       /* не частіше ніж раз на секунду */
      d->qos_last = now;

      GstFormat fmt = GST_FORMAT_UNDEFINED;
      guint64   processed = 0, dropped = 0;
      gst_message_parse_qos_stats (msg, &fmt, &processed, &dropped);
      if (fmt == GST_FORMAT_UNDEFINED)
        break;                       /* елемент лічби не веде — рахувати нема чого */

      gint64  jitter = 0;
      gdouble proportion = 1.0;
      gint    quality = 0;
      gst_message_parse_qos_values (msg, &jitter, &proportion, &quality);

      gchar *path = src_path (msg);
      g_printerr ("QoS %s [%s]: оброблено %" G_GUINT64_FORMAT
                  ", викинуто %" G_GUINT64_FORMAT
                  "; запізнення %.1f мс, темп ×%.2f\n",
                  path, gst_format_get_name (fmt), processed, dropped,
                  jitter / 1e6, proportion);
      g_free (path);
      break;
    }
```

Три числа тут читаються по-різному. **Викинуто** — факт: стільки кадрів уже не побачив ніхто. **Запізнення** (`jitter`) — різниця між тим, коли буфер дійшов, і тим, коли він мав дійти; додатне означає «спізнився», і його величина каже, наскільки серйозно. **Темп** (`proportion`) — довгострокова оцінка того, у скільки разів треба змінити швидкість обробки проти нормальної, щоб триматися реального часу; значення понад одиницю означає, що конвеєр стабільно не встигає, а не спіткнувся один раз. Стала одиниця з поодинокими сплесками — це нормальна робота; двійка, яка тримається, — це нестача продуктивності, і далі йдеться вже про [затримку й буферизацію](book:media-vision/latency-and-buffering).

### Стани — тільки конвеєра

Повідомлення `STATE_CHANGED` постить **кожен** елемент на кожному переході. Конвеєр із дванадцяти елементів дає під п'ятдесят рядків на один пуск, і серед них губиться те єдине, що має значення. Нас цікавить лише перехід конвеєра як цілого, бо він оголошується тоді, коли всі всередині вже перейшли.

```c
    case GST_MESSAGE_STATE_CHANGED: {
      if (GST_MESSAGE_SRC (msg) != GST_OBJECT (d->pipeline))
        break;                       /* стани окремих елементів — не наша справа */

      GstState from, to, pending;
      gst_message_parse_state_changed (msg, &from, &to, &pending);
      g_printerr ("конвеєр: %s → %s\n",
                  gst_element_state_get_name (from),
                  gst_element_state_get_name (to));

      if (to == GST_STATE_PLAYING && d->guard_id) {
        g_source_remove (d->guard_id);   /* доїхали — сторож більше не потрібен */
        d->guard_id = 0;
      }
      break;
    }
```

Тут же знімається сторожовий таймер. Це не оптимізація, а умова правильності: сторож, який вистрелив у конвеєрі, що вже грає, друкує неправдиву тривогу, і наступного разу їй ніхто не повірить.

Решта обробника — це кілька рядків диспетчеризації, які лишилося дописати навколо наведених гілок:

:::tabs
```c
static gboolean diag_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  Diag *d = data;
  (void) bus;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ERROR:
      diag_report (d, msg, "ПОМИЛКА");
      diag_dump (d, "error");        /* докази — у мілісекунду аварії */
      break;
    case GST_MESSAGE_WARNING:
      diag_report (d, msg, "ПОПЕРЕДЖЕННЯ");
      break;
    case GST_MESSAGE_INFO:
      diag_report (d, msg, "ВІДОМІСТЬ");
      break;

    /* … гілки ELEMENT, QOS і STATE_CHANGED з блоків вище … */

    default:
      break;
  }
  return TRUE;    /* лишаємось підключеними; msg НЕ звільняємо — він позичений */
}
```
```py
    def _on_message(self, bus, msg, _unused):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            self._report(msg, "ПОМИЛКА")
            self._dump("error")                    # докази — у мілісекунду аварії

        elif t == Gst.MessageType.WARNING:
            self._report(msg, "ПОПЕРЕДЖЕННЯ")

        elif t == Gst.MessageType.INFO:
            self._report(msg, "ВІДОМІСТЬ")

        elif t == Gst.MessageType.ELEMENT:
            if GstPbutils.is_missing_plugin_message(msg):
                desc = GstPbutils.missing_plugin_message_get_description(msg)
                inst = GstPbutils.missing_plugin_message_get_installer_detail(msg)
                print(f"БРАКУЄ ПЛАГІНА: {desc}", file=sys.stderr)
                print(f"  рядок для встановлювача: {inst}", file=sys.stderr)
                self._dump("missing-plugin")

        elif t == Gst.MessageType.QOS:
            now = GLib.get_monotonic_time()
            if now - self.qos_last < 1_000_000:     # не частіше ніж раз на секунду
                return True
            self.qos_last = now

            fmt, processed, dropped = msg.parse_qos_stats()
            if fmt == Gst.Format.UNDEFINED:
                return True                          # елемент лічби не веде
            jitter, proportion, _quality = msg.parse_qos_values()
            print(f"QoS {self._src_path(msg)} [{fmt.value_nick}]: "
                  f"оброблено {processed}, викинуто {dropped}; "
                  f"запізнення {jitter / 1e6:.1f} мс, темп ×{proportion:.2f}",
                  file=sys.stderr)

        elif t == Gst.MessageType.STATE_CHANGED:
            if msg.src is not self.pipeline:
                return True                          # стани окремих елементів — не наша справа
            old, new, _pending = msg.parse_state_changed()
            print(f"конвеєр: {Gst.Element.state_get_name(old)} → "
                  f"{Gst.Element.state_get_name(new)}", file=sys.stderr)
            if new == Gst.State.PLAYING and self.guard_id:
                GLib.source_remove(self.guard_id)     # доїхали — сторож не потрібен
                self.guard_id = 0

        return True                                  # лишаємось підключеними
```
:::

### Сторож: що застає таймер о N-й секунді

Тепер найцінніша частина. Помилка сама себе оголошує — конвеєр, який просто **стоїть**, не оголошує нічого. Сторожовий таймер потрібен саме для другого випадку, і його доповідь має розводити три різні ситуації.

![Три доріжки станів у часі: одна доходить до PLAYING до спрацювання таймера, друга зупиняється в PAUSED, третя — у READY; вертикальний пунктир позначає N-ту секунду](/reference/media-vision/gstreamer/pipeline-debugging/img/proj-watchdog-verdicts.svg)

*Ті самі N секунд і той самий чорний екран дають три різні діагнози залежно від того, до якого стану конвеєр устиг дійти. Без сторожа вони не розрізняються ніяк.*

`PAUSED` за домовленістю означає, що перший буфер уже дійшов до стоку — тому «застряг у `PAUSED`» читається однозначно: між джерелом і стоком є місце, де перший кадр зупинився. `READY` означає, що ресурси відкрито, але дані ще не пішли, тож «застряг у `READY`» — це майже завжди джерело, яке не відкрилося. Що саме обіцяє кожен стан, розібрано у темі про [стани конвеєра](book:media-vision/states-lifecycle).

:::tabs
```c
/* Спрацьовує один раз, якщо за guard_sec секунд PLAYING так і не настав. */
static gboolean diag_guard (gpointer data)
{
  Diag *d = data;
  GstState cur = GST_STATE_VOID_PENDING, pending = GST_STATE_VOID_PENDING;

  /* НУЛЬОВА витримка: питаємо, що є ЗАРАЗ, і не чекаємо ні миті.
     GST_CLOCK_TIME_NONE тут означало б «висни разом із конвеєром». */
  GstStateChangeReturn ret = gst_element_get_state (d->pipeline, &cur, &pending, 0);

  g_printerr ("СТОРОЖ: за %u с конвеєр не дійшов до PLAYING\n", d->guard_sec);
  g_printerr ("  зараз:   %s\n", gst_element_state_get_name (cur));
  g_printerr ("  у черзі: %s\n", gst_element_state_get_name (pending));
  g_printerr ("  перехід: %s\n", gst_element_state_change_return_get_name (ret));

  if (cur == GST_STATE_PAUSED && !d->is_live)
    g_printerr ("  → перший буфер не дійшов до стоку: розрив десь між ними\n");
  else if (cur == GST_STATE_PAUSED)
    g_printerr ("  → джерело живе, PAUSED тут не діагноз: дивись, чому нема PLAYING\n");
  else if (cur == GST_STATE_READY)
    g_printerr ("  → не вийшли з READY: джерело не відкрилося\n");
  else if (cur == GST_STATE_NULL)
    g_printerr ("  → конвеєр у NULL: set_state або не викликали, або він відкотився\n");

  diag_dump (d, "stuck");
  d->guard_id = 0;
  return G_SOURCE_REMOVE;      /* доповіли один раз — далі не набридаємо */
}
```
```py
    def _guard(self):
        """Спрацьовує один раз, якщо за guard_sec секунд PLAYING так і не настав."""
        # НУЛЬОВА витримка: питаємо, що є ЗАРАЗ, і не чекаємо ні миті.
        # Gst.CLOCK_TIME_NONE тут означало б «висни разом із конвеєром».
        ret, cur, pending = self.pipeline.get_state(0)

        print(f"СТОРОЖ: за {self.guard_sec} с конвеєр не дійшов до PLAYING",
              file=sys.stderr)
        print(f"  зараз:   {Gst.Element.state_get_name(cur)}", file=sys.stderr)
        print(f"  у черзі: {Gst.Element.state_get_name(pending)}", file=sys.stderr)
        print(f"  перехід: {Gst.Element.state_change_return_get_name(ret)}",
              file=sys.stderr)

        if cur == Gst.State.PAUSED and not self.is_live:
            print("  → перший буфер не дійшов до стоку: розрив десь між ними",
                  file=sys.stderr)
        elif cur == Gst.State.PAUSED:
            print("  → джерело живе, PAUSED тут не діагноз: дивись, чому нема PLAYING",
                  file=sys.stderr)
        elif cur == Gst.State.READY:
            print("  → не вийшли з READY: джерело не відкрилося", file=sys.stderr)
        elif cur == Gst.State.NULL:
            print("  → конвеєр у NULL: set_state або не викликали, або він відкотився",
                  file=sys.stderr)

        self._dump("stuck")
        self.guard_id = 0
        return GLib.SOURCE_REMOVE          # доповіли один раз — далі не набридаємо
```
:::

Поле `pending` тут не менш промовисте за `cur`. `PAUSED` із порожньою чергою (`VOID_PENDING`) означає, що конвеєр дійшов до `PAUSED` і **зупинився там навмисно** — ніхто не просив його йти далі. `PAUSED` із `PLAYING` у черзі означає, що просили, але перехід не завершується. Це знову два різні діагнози: перший — помилка в коді програми, другий — затик у самому конвеєрі.

### Пуск: `NO_PREROLL` — не помилка

Пуск робиться у два кроки не з обережності. Відповідь на перший крок — єдиний надійний спосіб дізнатися, чи джерело живе, а від цього залежить, який вирок має право виносити сторож.

:::tabs
```c
/* Пуск із розбором відповіді. FALSE — конвеєр навіть не почав. */
static gboolean diag_start (Diag *d)
{
  GstStateChangeReturn ret = gst_element_set_state (d->pipeline, GST_STATE_PAUSED);

  if (ret == GST_STATE_CHANGE_NO_PREROLL) {
    d->is_live = TRUE;
    g_printerr ("джерело живе: прероллу не буде, ASYNC_DONE теж не прийде\n");
  }

  if (ret != GST_STATE_CHANGE_FAILURE)
    ret = gst_element_set_state (d->pipeline, GST_STATE_PLAYING);

  if (ret == GST_STATE_CHANGE_FAILURE) {
    /* Помилка вже на шині, але головний цикл ще не крутиться, і стеження,
       хоч і приєднане, не спрацює. Забираємо руками — тією ж функцією. */
    GstMessage *msg = gst_bus_timed_pop_filtered (d->bus, 0, GST_MESSAGE_ERROR);
    if (msg) {
      diag_report (d, msg, "ПОМИЛКА ПУСКУ");
      gst_message_unref (msg);      /* а ЦЕ повідомлення наше — звільняємо */
    } else {
      g_printerr ("пуск не вдався, а помилки на шині немає\n");
    }
    diag_dump (d, "start-failed");
    return FALSE;
  }
  return TRUE;
}
```
```py
    def start(self):
        """Пуск із розбором відповіді. False — конвеєр навіть не почав."""
        ret = self.pipeline.set_state(Gst.State.PAUSED)

        if ret == Gst.StateChangeReturn.NO_PREROLL:
            self.is_live = True
            print("джерело живе: прероллу не буде, ASYNC_DONE теж не прийде",
                  file=sys.stderr)

        if ret != Gst.StateChangeReturn.FAILURE:
            ret = self.pipeline.set_state(Gst.State.PLAYING)

        if ret == Gst.StateChangeReturn.FAILURE:
            # Помилка вже на шині, але головний цикл ще не крутиться, і стеження,
            # хоч і приєднане, не спрацює. Забираємо руками — тією ж функцією.
            msg = self.bus.timed_pop_filtered(0, Gst.MessageType.ERROR)
            if msg is not None:
                self._report(msg, "ПОМИЛКА ПУСКУ")
            else:
                print("пуск не вдався, а помилки на шині немає", file=sys.stderr)
            self._dump("start-failed")
            return False
        return True
```
:::

`NO_PREROLL` — це відповідь камери, мікрофона чи мережевого потоку: даних наперед узяти нізвідки, вони існують лише в реальному часі. Програма, яка тлумачить це значення як невдачу, відмовляється працювати з живими джерелами. Програма, яка його ігнорує, чекає на `ASYNC_DONE`, якого не буде ніколи, — і висить не через несправність, а через власне очікування неможливого.

Гілка `FAILURE` — місце, де більшість прикладів обриваються рядком «не вдалося запустити конвеєр». Помилка на шині вже лежить: елемент устиг її запостити просто всередині `set_state()`. Але головний цикл іще не крутиться, і стеження не спрацює ніколи, бо програма зараз піде у вихід. Один виклик `gst_bus_timed_pop_filtered()` із нульовою витримкою забирає її звідти, і вона друкується так само докладно, як усі інші.

### Складання

:::tabs
```c
/* Тека для графів. Викликати ДО gst_init() — саме там читається змінна. */
static void diag_setup_dot_dir (const gchar *dir)
{
  g_mkdir_with_parents (dir, 0755);      /* GStreamer теку НЕ створює */
  g_setenv ("GST_DEBUG_DUMP_DOT_DIR", dir, TRUE);
}

int main (int argc, char **argv)
{
  if (argc < 2) {
    g_printerr ("вжиток: %s \"<опис конвеєра для gst-launch>\"\n", argv[0]);
    return 2;
  }

  diag_setup_dot_dir ("/tmp/gstdiag");   /* ПЕРЕД gst_init */
  gst_init (&argc, &argv);

  GError *perr = NULL;
  GstElement *pipeline = gst_parse_launch (argv[1], &perr);
  if (!pipeline) {
    g_printerr ("конвеєр не розібрано: %s\n", perr->message);
    g_clear_error (&perr);
    return 1;
  }

  GMainLoop *loop = g_main_loop_new (NULL, FALSE);
  Diag diag = { 0 };
  diag_attach (&diag, pipeline, "cam0", 10);   /* сторож на 10 секунд */

  if (diag_start (&diag))
    g_main_loop_run (loop);                    /* без цього рядка обв'язка мертва */

  gst_element_set_state (pipeline, GST_STATE_NULL);
  diag_detach (&diag);
  gst_object_unref (pipeline);
  g_main_loop_unref (loop);
  return 0;
}
```
```py
if __name__ == "__main__":
    import os

    if len(sys.argv) < 2:
        print(f'вжиток: {sys.argv[0]} "<опис конвеєра для gst-launch>"', file=sys.stderr)
        sys.exit(2)

    os.makedirs("/tmp/gstdiag", exist_ok=True)              # GStreamer теку НЕ створює
    os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp/gstdiag"   # ПЕРЕД Gst.init
    Gst.init(None)

    loop = GLib.MainLoop()
    pipeline = Gst.parse_launch(sys.argv[1])

    diag = Diag(pipeline, "cam0", guard_sec=10)             # сторож на 10 секунд
    if diag.start():
        loop.run()                                          # без цього рядка обв'язка мертва

    pipeline.set_state(Gst.State.NULL)
    diag.detach()
```
:::

```sh
gcc gstdiag.c -o gstdiag $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-pbutils-1.0)
./gstdiag "rtspsrc location=rtsp://cam/stream ! decodebin ! autovideosink"
```

Пакунок `gstreamer-pbutils-1.0` приїжджає разом із заголовками `gst-plugins-base` — окремо його встановлювати не треба, але в рядку складання він має бути, інакше розпізнавання браку плагінів не злінкується.

## Пастки

П'ять способів отримати обв'язку, яка виглядає працездатною і не працює.

**Стеження без циклу.** `gst_bus_add_watch()` не запускає нічого — воно лише **чіпляє джерело подій** до типового головного контексту GLib. Доки цей контекст ніхто не обертає, обробник не викликається жодного разу, повідомлення накопичуються в черзі, і програма мовчить так само переконливо, як мовчала б без обв'язки. Найчастіше це трапляється в застосунку, у якого вже є **свій** цикл подій — власний сервер, чужий набір віджетів, — бо той контекст не є типовим. Ліків два: підняти `GMainLoop` в окремій нитці або взагалі не приєднувати стеження, а вичерпувати шину `gst_bus_pop()` із таймера свого циклу — і тоді власником повідомлень стаєте ви, з обов'язком звільнити кожне. Коли контекст свій, але не типовий, є третій шлях: `gst_bus_create_watch()` віддає джерело, яке ви самі приєднуєте куди треба. Механіка того, чому джерело подій без циклу — просто структура в пам'яті, розібрана в темі про [цикл подій](book:programming/event-loop).

**Блокувальний запит стану.** `gst_element_get_state (pipeline, &s, &p, GST_CLOCK_TIME_NONE)` чекає, доки перехід завершиться — тобто **вічно**, якщо конвеєр застряг. Сторож, написаний так, помирає разом із тим, що мав спіймати. Гірше: якщо він викликається з нитки головного циклу, то заразом зупиняє й стеження за шиною, і та сама `ERROR`, яка все б пояснила, лишається непрочитаною назавжди. Нуль означає «скажи, що є зараз», і не блокує ніколи; скінченна витримка на кшталт `100 * GST_MSECOND` доречна лише там, де ви справді хочете почекати й готові до того, що не дочекаєтеся.

**Забутий `g_free`.** `gst_message_parse_error()` віддає **у власність** і `GError`, і зневаджувальний рядок; те саме роблять `gst_object_get_path_string()` та обидві функції розбору браку плагінів. На помилці, що трапляється раз за запуск, витік невидимий. На `WARNING`, який деякі елементи постять на кожен проблемний буфер, він стає помітним за години. Безпечніший близнюк `g_error_free()` — це `g_clear_error()`: він і `NULL` переживе, і вказівник по собі занулить. Зворотна помилка так само реальна: `GstMessage`, що прийшов у стеження, **позичений**, і `gst_message_unref()` на нього — подвійне звільнення, яке виявиться десь у надрах наступного повідомлення. Своїм повідомлення стає лише тоді, коли ви забрали його `pop`-ом самі.

**Теки, якої немає.** `GST_DEBUG_DUMP_DOT_DIR` не створюється — ні бібліотекою, ні макросом. Указали неіснуючий шлях, і скидання графа мовчки не робить нічого: ні попередження, ні коду помилки, ні рядка в журналі. Друга половина тієї ж пастки — час: змінну читають під час `gst_init()`, тож виставляти її після ініціалізації безглуздо. Якщо теки взагалі не має бути (незмінна файлова система, немає куди писати), є обхід: `gst_debug_bin_to_dot_data()` повертає той самий опис графа **рядком** і жодних змінних середовища не питає — далі його можна покласти у власний журнал, відправити по мережі або втиснути в повідомлення про аварію.

**Макроси, що компілюються в ніщо.** Обидва скидачі графа — це макроси, і в бібліотеці, зібраній без діагностики (`GST_DISABLE_GST_DEBUG`, звична економія в урізаних вбудованих збірках), вони розкриваються в порожнечу. Разом із ними перестає діяти й `GST_DEBUG` — журналу теж не буде. Ззовні це виглядає як обв'язка, що бездоганно друкує повідомлення й ніколи не залишає жодного графа. Тому перевірку варто зробити гучною **на старті**, а не на місці аварії: `#ifdef GST_DISABLE_GST_DEBUG` у діагностичній функції коштує нуль і рятує від довгого здивування. У Python цієї пастки в такій формі немає — там викликається сама функція, а не макрос, — але якщо діагностику вимкнено в самій бібліотеці, функція буде порожньою заглушкою.

І шоста, яка не належить до GStreamer, але з'їдає ту саму годину: **сторож живе в тому ж циклі, що й усе інше**. Він ловить конвеєр, який стоїть, — і не ловить програму, яка стоїть, бо разом із нею стоїть і він сам. Для другого випадку потрібен незалежний спостерігач: окрема нитка з власним контекстом або зовнішній [сторожовий таймер](book:programming/watchdog), який дивиться на процес ззовні.

## Що це коштує

Дорога даних не зачіпається взагалі: шина — окремий канал, і жоден буфер крізь обв'язку не проходить. Ціна складається з трьох дрібних доданків. Одне джерело подій у циклі й один таймер — константа, помітна хіба що в лічильнику дескрипторів. Одне виділення пам'яті на повідомлення шини: на здоровому конвеєрі це кілька штук за пуск і нуль потім, на конвеєрі, що не встигає, — десятки `QOS` за секунду, які й зрізає загорожа за часом.

Третій доданок єдиний вартий уваги: **скидання графа — це синхронний запис файлу**. Із прапорцем `SHOW_ALL` у файл іде повний перелік caps на кожному з'єднанні, і на розлогому конвеєрі це від кількох до кількох десятків кілобайт. Один запис у момент аварії — безкоштовно; той самий виклик із обробника `pad-added` на потоці, де пади з'являються постійно, — уже помітна витрата. Правило просте: скидати за подією, яка трапляється рідко, і ніколи — за подією, прив'язаною до буфера.
