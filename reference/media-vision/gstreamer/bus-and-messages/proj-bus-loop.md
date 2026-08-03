# ⚙️ Робочий цикл шини: програвач від першого елемента до чистої зупинки

Це повна програма — програвач одного посилання, байдуже, файл це чи мережа, — у якій шина не декорація, а несуча конструкція: тільки через неї програма дізнається, що потік скінчився, що декодер здався, що мережа не встигає й що затримку треба перерахувати. Приклади на десять рядків, де в обробнику стоять лише `ERROR` і `EOS`, працюють рівно доти, доки джерело локальне й справне; усе решта починається на першому ж `rtsp://`.

Основою беремо `uridecodebin` — джерело плюс декодер в одному елементі, який сам вибирає, чим читати `file://`, `http://` чи `rtsp://`, і сам знаходить потрібний декодер. Приймачі дописуємо ми, коли елемент повідомить, які потоки в матеріалі знайшлися. Далі весь код програми, окрім двох десятків рядків запуску, живе в колбеках.

## Шість подій, які мусить пережити програма

Перелічимо їх наперед, бо саме з них виростає структура коду.

**Помилка.** Файлу немає, сокет закрився, декодера в системі не встановлено. Розібрати треба обидві частини: `GError` — для людини, зневаджувальний рядок — для журналу. І перевести конвеєр у `NULL`, бо сам він не зупиниться.

**Кінець потоку.** Приймачі відзвітували всі до одного, конвеєр звів їхні звіти в один `EOS` — можна виходити.

**Зміна стану.** Корисна для журналу й для розуміння, де саме програма застрягла. Пастка тут у тому, що `STATE_CHANGED` постить **кожен** елемент на кожному переході: на десятку елементів це сорок повідомлень за один пуск. Нам потрібні лише ті, де джерело — сам конвеєр.

**Буферизація.** Мережеве джерело набирає запас і доповідає відсоток. Поки відсоток менший за сто, грати нічого — конвеєр треба тримати в `PAUSED`. Але живого джерела це не стосується: камера не зачекає, доки ми надолужимо.

**Затримка.** Елемент усередині перерахував свою латентність і просить розіслати нову спільну. Це прохання, і виконати його має застосунок.

**Попередження.** Щось пішло не так, але робота триває. Зупиняти конвеєр через `WARNING` — найдешевший спосіб зробити програму, яка падає на кожному подряпаному файлі.

## Стан застосунку: намір окремо, факт окремо

Найважливіше рішення в цій програмі — не в обробнику, а в структурі даних. Буферизація змушує нас перемикати конвеєр між `PAUSED` і `PLAYING` за чужою командою, і після кількох таких перемикань питання «а в якому стані ми зараз мали б бути?» стає невідповідним. Тому **намір** застосунку зберігається окремо від фактичного стану конвеєра: поле `target` каже, чого ми хочемо, і воно не змінюється від того, що джерело на секунду попросило паузи.

Поруч живуть ще два прапорці: `is_live` — чи конвеєр живий (з'ясуємо це під час пуску) і `buffering` — чи ми **зараз** усередині набору запасу, щоб не ставити паузу двічі й не знімати її, коли її ніхто не ставив.

Усе це разом одна структура, вказівник на яку ми передаємо в кожен колбек. Колбеки шини виконуються всі в одній нитці — тій, що крутить головний цикл, — тому замок їм не потрібен; про це варто пам'ятати, бо `pad-added` нижче виконується вже **не** в ній.

:::tabs
```c
#include <gst/gst.h>

typedef struct {
  GstElement *pipeline;
  GstBus     *bus;
  GMainLoop  *loop;
  guint       watch_id;

  GstState    target;      /* чого ми хочемо; буферизація цього не змінює */
  gboolean    is_live;     /* живий конвеєр: паузою не керуємо взагалі */
  gboolean    buffering;   /* зараз усередині набору запасу */
  int         exit_code;
} App;

/* Ім'я джерела повідомлення. Джерела може й не бути — тоді GST_OBJECT_NAME
   впаде на нульовому вказівнику, тому питаємо обережно. */
static const gchar *src_name (GstMessage *msg)
{
  GstObject *src = GST_MESSAGE_SRC (msg);
  return src ? GST_OBJECT_NAME (src) : "(без джерела)";
}

/* Обидва колбеки означено нижче; у файлі вони йдуть перед build(). */
static void     on_pad_added   (GstElement *dec, GstPad *pad, gpointer data);
static gboolean on_bus_message (GstBus *bus, GstMessage *msg, gpointer data);

static gboolean build (App *app, const gchar *uri)
{
  app->loop     = g_main_loop_new (NULL, FALSE);
  app->target   = GST_STATE_PLAYING;
  app->pipeline = gst_pipeline_new ("player");

  GstElement *dec = gst_element_factory_make ("uridecodebin", "dec");
  if (!dec) {
    g_printerr ("немає елемента uridecodebin — не встановлено gst-plugins-base\n");
    return FALSE;
  }
  g_object_set (dec, "uri", uri,
                     "use-buffering", TRUE,     /* без цього BUFFERING не постить */
                     NULL);
  gst_bin_add (GST_BIN (app->pipeline), dec);
  g_signal_connect (dec, "pad-added", G_CALLBACK (on_pad_added), app);

  app->bus      = gst_element_get_bus (app->pipeline);
  app->watch_id = gst_bus_add_watch (app->bus, on_bus_message, app);
  if (app->watch_id == 0) {
    g_printerr ("стеження не приєдналося: на шині вже є інше\n");
    return FALSE;
  }
  return TRUE;
}
```
```py
import sys
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib


class Player:
    def __init__(self, uri):
        self.loop = GLib.MainLoop()
        self.target = Gst.State.PLAYING   # чого ми хочемо; буферизація цього не змінює
        self.is_live = False              # живий конвеєр: паузою не керуємо взагалі
        self.buffering = False            # зараз усередині набору запасу
        self.exit_code = 0

        self.pipeline = Gst.Pipeline.new("player")
        dec = Gst.ElementFactory.make("uridecodebin", "dec")
        if dec is None:
            raise RuntimeError("немає елемента uridecodebin — не встановлено gst-plugins-base")
        dec.set_property("uri", uri)
        dec.set_property("use-buffering", True)
        self.pipeline.add(dec)
        dec.connect("pad-added", self.on_pad_added)

        self.bus = self.pipeline.get_bus()
        self.watch_id = self.bus.add_watch(GLib.PRIORITY_DEFAULT, self.on_message, None)
```
:::

Одна деталь у налаштуванні `uridecodebin` варта окремої згадки: `use-buffering` типово **вимкнено**. Без нього мережеве джерело мовчки набиратиме запас, і жодного `BUFFERING` ви не побачите — а потім здивуєтеся, чому картинка починається з ривка. Увімкнули — і елемент постить відсоток, поки набирає.

## Гілки на вимогу: `pad-added` приходить у чужій нитці

`uridecodebin` не знає наперед, що всередині матеріалу. Він відкриває джерело, розбирає контейнер, запускає декодери — і аж тоді, для кожного знайденого потоку, віддає назовні готовий pad із сигналом `pad-added`. Наше діло — подивитися на формат і добудувати відповідний хвіст.

Тут криється перша нагода все зіпсувати. `pad-added` — це **сигнал**, а не повідомлення з шини: він приходить не через чергу, а прямим викликом, у тій самій нитці, яка щойно розібрала контейнер. Малювати з нього щось на екрані не можна; довго думати в ньому теж не варто — доки ми думаємо, декодер стоїть. Робота з елементами конвеєра з цієї нитки, натомість, цілком дозволена, і саме її ми й робимо.

Друга нагода — порядок дій. Елемент, доданий у конвеєр, треба **спершу з'єднати й тільки потім** підтягнути його стан під конвеєр. Навпаки не виходить: запущений у порожнечу `queue` одразу впаде помилкою про непід'єднаний pad, і програма зупиниться на порожньому місці.

:::tabs
```c
/* Будує ланцюжок елементів, лінкує його й підтягує стан під конвеєр.
   Повертає вхідний pad першого елемента — його звільняє викликач. */
static GstPad *add_branch (App *app, const gchar *const *factories)
{
  GstElement *chain[4] = { NULL, NULL, NULL, NULL };
  guint n = 0;

  for (; n < G_N_ELEMENTS (chain) && factories[n] != NULL; n++) {
    chain[n] = gst_element_factory_make (factories[n], NULL);
    if (!chain[n]) {
      g_printerr ("бракує елемента «%s» — не встановлено плагін\n", factories[n]);
      return NULL;
    }
    gst_bin_add (GST_BIN (app->pipeline), chain[n]);   /* конвеєр забрав посилання */
    if (n > 0 && !gst_element_link (chain[n - 1], chain[n])) {
      g_printerr ("не з'єдналися %s і %s\n", factories[n - 1], factories[n]);
      return NULL;
    }
  }

  /* стан підтягуємо ТІЛЬКИ після з'єднання всього ланцюжка */
  for (guint i = 0; i < n; i++)
    gst_element_sync_state_with_parent (chain[i]);

  return gst_element_get_static_pad (chain[0], "sink");
}

/* Викликається в НИТЦІ ПОТОКУ uridecodebin, не в головній. */
static void on_pad_added (GstElement *dec, GstPad *pad, gpointer data)
{
  static const gchar *const video[] = { "queue", "videoconvert", "autovideosink", NULL };
  static const gchar *const audio[] = { "queue", "audioconvert", "audioresample",
                                        "autoaudiosink", NULL };
  App *app = data;

  GstCaps *caps = gst_pad_get_current_caps (pad);
  if (!caps)
    caps = gst_pad_query_caps (pad, NULL);
  const gchar *media = gst_structure_get_name (gst_caps_get_structure (caps, 0));

  const gchar *const *want = NULL;
  const gchar *label = NULL;
  if (g_str_has_prefix (media, "video/"))      { want = video; label = "відео"; }
  else if (g_str_has_prefix (media, "audio/")) { want = audio; label = "звук";  }
  gst_caps_unref (caps);            /* після цього рядка media вже недійсний */

  if (!want)
    return;                         /* субтитри й службові потоки не беремо */

  GstPad *sink = add_branch (app, want);
  if (!sink)
    return;
  if (gst_pad_link (pad, sink) != GST_PAD_LINK_OK)
    g_printerr ("гілку «%s» не приєднано\n", label);
  gst_object_unref (sink);
}
```
```py
    def add_branch(self, factories):
        """Будує ланцюжок, лінкує його й підтягує стан під конвеєр.
        Повертає вхідний pad першого елемента."""
        chain = []
        for name in factories:
            element = Gst.ElementFactory.make(name)
            if element is None:
                print(f"бракує елемента «{name}» — не встановлено плагін", file=sys.stderr)
                return None
            self.pipeline.add(element)
            if chain and not chain[-1].link(element):
                print(f"не з'єдналися {chain[-1].name} і {name}", file=sys.stderr)
                return None
            chain.append(element)

        # стан підтягуємо ТІЛЬКИ після з'єднання всього ланцюжка
        for element in chain:
            element.sync_state_with_parent()
        return chain[0].get_static_pad("sink")

    def on_pad_added(self, dec, pad):
        """Викликається в НИТЦІ ПОТОКУ uridecodebin, не в головній."""
        caps = pad.get_current_caps() or pad.query_caps(None)
        media = caps.get_structure(0).get_name()

        if media.startswith("video/"):
            want, label = ["queue", "videoconvert", "autovideosink"], "відео"
        elif media.startswith("audio/"):
            want, label = ["queue", "audioconvert", "audioresample", "autoaudiosink"], "звук"
        else:
            return                       # субтитри й службові потоки не беремо

        sink = self.add_branch(want)
        if sink is None:
            return
        if pad.link(sink) != Gst.PadLinkReturn.OK:
            print(f"гілку «{label}» не приєднано", file=sys.stderr)
```
:::

`queue` на початку кожної гілки — не прикраса. Він розриває ланцюг і додає власну нитку, тож відео й звук перестають чекати одне на одного, а повільний приймач не гальмує декодер. Без нього дві гілки з одного демультиплексора рано чи пізно взаємно заблокуються.

> 🔧 **Навіщо це.** Якщо ви бачите «конвеєр запустився, стан `PLAYING`, а вікна немає» — перше, що треба перевірити, це чи взагалі приходив `pad-added`. Найчастіша причина мовчання — джерело не відкрилося, і тоді на шині вже лежить `ERROR`, який нікому забрати. Друга за частотою — гілка побудована, але `sync_state_with_parent` не викликано, і вся вона так і лишилася в `NULL`, поки решта конвеєра грає.

## Обробник шини — серце програми

Тепер власне те, заради чого все затівалося. Одна функція, один `switch`, і в кожній гілці — рішення, а не просто друк.

:::tabs
```c
/* Розбір помилки. Повідомлення НЕ звільняє — власник у різних дорогах різний. */
static void report_error (GstMessage *msg)
{
  GError *err = NULL;
  gchar  *dbg = NULL;
  gst_message_parse_error (msg, &err, &dbg);

  g_printerr ("ПОМИЛКА від %s: %s\n", src_name (msg), err->message);
  g_printerr ("  домен %s, код %d\n", g_quark_to_string (err->domain), err->code);

  if (g_error_matches (err, GST_RESOURCE_ERROR, GST_RESOURCE_ERROR_NOT_FOUND))
    g_printerr ("  → за цією адресою джерела немає\n");
  else if (g_error_matches (err, GST_STREAM_ERROR, GST_STREAM_ERROR_CODEC_NOT_FOUND))
    g_printerr ("  → у системі немає плагіна-декодера для цього формату\n");

  g_printerr ("  зневадження: %s\n", dbg ? dbg : "(немає)");

  g_clear_error (&err);
  g_free (dbg);
}

static gboolean on_bus_message (GstBus *bus, GstMessage *msg, gpointer data)
{
  App *app = data;

  switch (GST_MESSAGE_TYPE (msg)) {

    case GST_MESSAGE_ERROR:
      report_error (msg);
      app->exit_code = 1;
      g_main_loop_quit (app->loop);       /* конвеєр сам не спиниться */
      break;

    case GST_MESSAGE_EOS:
      g_print ("кінець потоку\n");
      g_main_loop_quit (app->loop);
      break;

    case GST_MESSAGE_WARNING: {
      GError *err = NULL;
      gchar  *dbg = NULL;
      gst_message_parse_warning (msg, &err, &dbg);
      g_printerr ("попередження від %s: %s (%s)\n",
                  src_name (msg), err->message, dbg ? dbg : "—");
      g_clear_error (&err);
      g_free (dbg);
      break;                              /* робота триває — не зупиняємо */
    }

    case GST_MESSAGE_STATE_CHANGED: {
      if (GST_MESSAGE_SRC (msg) != GST_OBJECT (app->pipeline))
        break;                            /* стани окремих елементів нас не цікавлять */
      GstState from, to, pending;
      gst_message_parse_state_changed (msg, &from, &to, &pending);
      g_print ("конвеєр: %s → %s\n",
               gst_element_state_get_name (from), gst_element_state_get_name (to));
      break;
    }

    case GST_MESSAGE_BUFFERING: {
      if (app->is_live)
        break;                            /* живому джерелу пауза лише зашкодить */
      gint percent = 0;
      gst_message_parse_buffering (msg, &percent);
      g_print ("буферизація %3d%%\n", percent);

      if (percent < 100) {
        if (!app->buffering && app->target == GST_STATE_PLAYING)
          gst_element_set_state (app->pipeline, GST_STATE_PAUSED);
        app->buffering = TRUE;
      } else if (app->buffering) {
        app->buffering = FALSE;
        if (app->target == GST_STATE_PLAYING)
          gst_element_set_state (app->pipeline, GST_STATE_PLAYING);
      }
      break;
    }

    case GST_MESSAGE_LATENCY:
      g_print ("перерахунок затримки на прохання %s\n", src_name (msg));
      gst_bin_recalculate_latency (GST_BIN (app->pipeline));
      break;

    case GST_MESSAGE_CLOCK_LOST:
      /* годинник зник; новий вибереться на наступному вході в PLAYING */
      gst_element_set_state (app->pipeline, GST_STATE_PAUSED);
      gst_element_set_state (app->pipeline, GST_STATE_PLAYING);
      break;

    default:
      break;
  }

  return TRUE;      /* лишаємось підключеними; msg НЕ звільняємо — він позичений */
}
```
```py
    def report_error(self, msg):
        """Розбір помилки. Повідомлення не звільняє — власник у різних дорогах різний."""
        err, dbg = msg.parse_error()

        print(f"ПОМИЛКА від {msg.src.name}: {err.message}", file=sys.stderr)
        print(f"  домен {err.domain}, код {err.code}", file=sys.stderr)

        if err.domain == "gst-resource-error-quark" and err.code == Gst.ResourceError.NOT_FOUND:
            print("  → за цією адресою джерела немає", file=sys.stderr)
        elif err.domain == "gst-stream-error-quark" and err.code == Gst.StreamError.CODEC_NOT_FOUND:
            print("  → у системі немає плагіна-декодера для цього формату", file=sys.stderr)

        print(f"  зневадження: {dbg or '(немає)'}", file=sys.stderr)

    def on_message(self, bus, msg, _unused):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            self.report_error(msg)
            self.exit_code = 1
            self.loop.quit()                      # конвеєр сам не спиниться

        elif t == Gst.MessageType.EOS:
            print("кінець потоку")
            self.loop.quit()

        elif t == Gst.MessageType.WARNING:
            err, dbg = msg.parse_warning()
            print(f"попередження від {msg.src.name}: {err.message} ({dbg or '—'})",
                  file=sys.stderr)                # робота триває — не зупиняємо

        elif t == Gst.MessageType.STATE_CHANGED:
            if msg.src is not self.pipeline:
                return True                       # стани окремих елементів нас не цікавлять
            old, new, _pending = msg.parse_state_changed()
            print(f"конвеєр: {Gst.Element.state_get_name(old)} → "
                  f"{Gst.Element.state_get_name(new)}")

        elif t == Gst.MessageType.BUFFERING:
            if self.is_live:
                return True                       # живому джерелу пауза лише зашкодить
            percent = msg.parse_buffering()
            print(f"буферизація {percent:3d}%")

            if percent < 100:
                if not self.buffering and self.target == Gst.State.PLAYING:
                    self.pipeline.set_state(Gst.State.PAUSED)
                self.buffering = True
            elif self.buffering:
                self.buffering = False
                if self.target == Gst.State.PLAYING:
                    self.pipeline.set_state(Gst.State.PLAYING)

        elif t == Gst.MessageType.LATENCY:
            print(f"перерахунок затримки на прохання {msg.src.name}")
            self.pipeline.recalculate_latency()

        elif t == Gst.MessageType.CLOCK_LOST:
            # годинник зник; новий вибереться на наступному вході в PLAYING
            self.pipeline.set_state(Gst.State.PAUSED)
            self.pipeline.set_state(Gst.State.PLAYING)

        return True                               # лишаємось підключеними
```
:::

Три рядки в цьому коді варті окремого погляду.

Порівняння `GST_MESSAGE_SRC (msg) != GST_OBJECT (app->pipeline)` — той самий фільтр, без якого журнал перетворюється на кашу. Кожен елемент звітує про свій перехід, і на звичайному відеофайлі це три-чотири десятки рядків на пуск; нас цікавить лише перехід конвеєра як цілого, бо саме він означає «усе всередині вже перейшло». Що насправді відбувається на кожному з переходів — розписано у статті про [стани конвеєра](book:media-vision/states-lifecycle).

`gst_bin_recalculate_latency()` на `LATENCY` — рівно те, що робить `gst-launch-1.0`, коли друкує своє «Redistribute latency…». Повідомлення означає, що якийсь елемент (майже завжди це буфер джитера на мережевому вході) змінив свою затримку, і спільну треба зібрати заново та розіслати всім. Не зробити цього означає розсинхронізацію відео зі звуком, яка з'являється через хвилину після старту й на яку нічого не вказує; звідки береться сама затримка, розібрано у статті про [затримку й буферизацію](book:media-vision/latency-and-buffering).

`return TRUE` наприкінці — це «лишити стеження підключеним». Повернене `FALSE` знімає джерело подій із циклу, і далі шина мовчить назавжди. Помилитися тут легко, бо ця функція виглядає як звичайний обробник, у якому повернене значення нічого не важить.

## Буферизація: чому паузу ставить застосунок

Найтонше місце програми — саме тут, і воно тонке не через код, а через те, що правильна поведінка залежить від виду джерела.

![Три різні реакції на BUFFERING: живий конвеєр не чіпаємо, для решти — пауза, доки відсоток не дійде до ста](/reference/media-vision/gstreamer/bus-and-messages/img/proj-buffering-cycle.svg)

*Реакція на BUFFERING: намір застосунку весь час лишається `PLAYING`, а фактичний стан конвеєра коливається під нього.*

Для джерела із запасом — файл через мережу, потік по HTTP — логіка проста. Відсоток менший за сто означає, що даних наразі мало; якщо не спинитися, приймач догляне до кінця наявного й гратиме тишу з застиглим кадром. Тому: перший `BUFFERING` із неповним відсотком → `PAUSED`; сотий відсоток → назад у `PLAYING`. Прапорець `buffering` тут потрібен, щоб не ставити паузу на кожному з десятків повідомлень і не знімати її, коли ми її не ставили.

Для **живого** джерела те саме означало б протилежне. Камера не спиняється від того, що ми поставили паузу: вона й далі віддає кадри в реальному часі, а ми їх не забираємо. Через п'ять секунд паузи ми відстанемо на п'ять секунд і вже ніколи не наздоженемо — запас перетвориться на постійну затримку. Тому для живого конвеєра `BUFFERING` — суто відомість: показати смужку в інтерфейсі можна, чіпати стан не можна.

Розпізнати живий конвеєр можна двома незалежними способами. Основний — відповідь на перший перехід у `PAUSED` (про це нижче). Додатковий — саме повідомлення: `gst_message_parse_buffering_stats()` віддає режим, і `GST_BUFFERING_LIVE` серед його значень означає рівно те, що написано. Другий спосіб зручний, коли в одному застосунку живі й неживі джерела перемішані; чому мережеві джерела майже завжди живі, а `http://` — ні, розібрано у статті про [мережеві джерела](book:media-vision/network-sources).

## Пуск: `PAUSED` як розвідка

Запустити конвеєр можна одним викликом одразу в `PLAYING`. Ми робимо це у два кроки — і не з обережності, а тому, що перший крок **повертає відповідь на питання, чи конвеєр живий**.

Перехід у `PAUSED` змушує конвеєр домовитися про формати й підготувати перший кадр. Звичайне джерело це вміє, і виклик повертає `GST_STATE_CHANGE_ASYNC` — «роблю, скажу згодом». Живе джерело підготувати кадр наперед не може принципово: кадру ще не існує, він з'явиться, коли камера його зніме. Саме тому воно відповідає окремим значенням `GST_STATE_CHANGE_NO_PREROLL`, і це найнадійніший наявний спосіб дізнатися вид конвеєра.

:::tabs
```c
int main (int argc, char **argv)
{
  gst_init (&argc, &argv);
  if (argc < 2) {
    g_printerr ("вжиток: %s <uri>\n", argv[0]);
    return 2;
  }

  App app = { 0 };
  if (!build (&app, argv[1]))
    return 1;

  GstStateChangeReturn ret = gst_element_set_state (app.pipeline, GST_STATE_PAUSED);

  if (ret == GST_STATE_CHANGE_FAILURE) {
    /* головного циклу ще нема, забрати повідомлення нікому — беремо самі */
    GstMessage *msg = gst_bus_timed_pop_filtered (app.bus, 0, GST_MESSAGE_ERROR);
    if (msg) {
      report_error (msg);
      gst_message_unref (msg);        /* це повідомлення НАШЕ */
    } else {
      g_printerr ("конвеєр не пішов у PAUSED, а помилки на шині немає\n");
    }
    app.exit_code = 1;
  } else {
    app.is_live = (ret == GST_STATE_CHANGE_NO_PREROLL);
    gst_element_set_state (app.pipeline, GST_STATE_PLAYING);
    g_main_loop_run (app.loop);       /* уся програма живе тут */
  }

  /* однаковий шлях і після помилки, і після EOS */
  gst_element_set_state (app.pipeline, GST_STATE_NULL);
  gst_bus_remove_watch (app.bus);
  gst_object_unref (app.bus);
  gst_object_unref (app.pipeline);
  g_main_loop_unref (app.loop);
  return app.exit_code;
}
```
```py
    def run(self):
        ret = self.pipeline.set_state(Gst.State.PAUSED)

        if ret == Gst.StateChangeReturn.FAILURE:
            # головного циклу ще нема, забрати повідомлення нікому — беремо самі
            msg = self.bus.timed_pop_filtered(0, Gst.MessageType.ERROR)
            if msg is not None:
                self.report_error(msg)   # звільняє зв'язувач, коли обгортка помре
            else:
                print("конвеєр не пішов у PAUSED, а помилки на шині немає", file=sys.stderr)
            self.exit_code = 1
        else:
            self.is_live = (ret == Gst.StateChangeReturn.NO_PREROLL)
            self.pipeline.set_state(Gst.State.PLAYING)
            self.loop.run()              # уся програма живе тут

        # однаковий шлях і після помилки, і після EOS
        self.pipeline.set_state(Gst.State.NULL)
        self.bus.remove_watch()
        return self.exit_code


def main():
    Gst.init(None)
    if len(sys.argv) < 2:
        print(f"вжиток: {sys.argv[0]} <uri>", file=sys.stderr)
        return 2
    return Player(sys.argv[1]).run()


if __name__ == "__main__":
    sys.exit(main())
```
:::

Гілка `FAILURE` — місце, де більшість прикладів обриваються рядком «не вдалося запустити конвеєр», і саме через неї найчастіше не видно причини. Помилка на шині вже лежить: елемент устиг її запостити просто всередині `set_state()`. Але головний цикл іще не крутиться, і стеження, хоч і підключене, не спрацює ніколи — програма ж зараз піде у вихід. Тому ми дістаємо повідомлення руками, тим самим `gst_bus_timed_pop_filtered()` із нульовою витримкою, і віддаємо в **ту саму** функцію розбору. Ціна цього кроку — один рядок і обов'язок звільнити, про який далі.

Збирається все звичайно:

```
# gstreamer-video-1.0 знадобиться синхронному обробникові нижче
gcc player.c -o player $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-video-1.0)

./player file:///шлях/до/файлу.mp4
./player rtsp://camera.local/stream
```

## Хто звільняє повідомлення

Одне й те саме `GstMessage` в цій програмі проходить трьома різними дорогами, і власник у кожної свій. Плутанина тут дає або подвійне звільнення (аварія одразу), або витік (аварія за кілька годин).

**Колбек стеження.** Повідомлення позичене. Шина зробить `unref` сама, щойно ваша функція поверне керування. Викликати `gst_message_unref()` тут — помилка, і виявиться вона не на цьому рядку, а десь у надрах наступного повідомлення.

**Ручний `pop`.** `gst_bus_pop()` і `gst_bus_timed_pop_filtered()` передають повідомлення **у власність**. Не звільнити — витік; у програмі, що опитує шину в циклі, це витік із рівномірним зростанням пам'яті.

**Синхронний обробник, що повернув `GST_BUS_DROP`.** Повідомлення з дороги зникло, у чергу не потрапить, більше про нього не згадає ніхто — крім вас. `gst_message_unref()` обов'язковий. `GST_BUS_PASS` і `GST_BUS_ASYNC`, навпаки, нічого не забирають: повідомлення йде далі своїм шляхом і звільниться там.

У Python усі три випадки виглядають однаково — обгортка тримає посилання й відпускає його разом зі збиранням сміття. Це зручно рівно доти, доки ви не переносите готовий алгоритм із Python у C: там `pop` без `unref` компілюється мовчки. Механіка, за якою це працює, — звичайний [підрахунок посилань](book:programming/reference-counting).

## Синхронний обробник: вікно потрібне негайно

Черга дає спокій, але забирає час, і є одна обставина, у якій часу немає. Відеоприймач, дійшовши до першого кадру, мусить знати, у яке вікно малювати. Якщо не сказати йому цього **до** того, як він продовжить, він створить власне вікно — і замість картинки всередині вашого інтерфейсу на екрані вискочить окрема рамка. Прочитати повідомлення з черги вже запізно: до того моменту зайве вікно існує.

Тому обробник тут окремий, синхронний — його шина кличе негайно, у нитці, що постила, ще до всякої черги:

:::tabs
```c
#include <gst/video/videooverlay.h>

static guintptr window_handle;    /* заповнює віконна система до пуску конвеєра */

static GstBusSyncReply on_sync_message (GstBus *bus, GstMessage *msg, gpointer data)
{
  if (!gst_is_video_overlay_prepare_window_handle_message (msg))
    return GST_BUS_PASS;          /* решта — звичайним шляхом, у чергу */

  gst_video_overlay_set_window_handle (GST_VIDEO_OVERLAY (GST_MESSAGE_SRC (msg)),
                                       window_handle);
  gst_message_unref (msg);        /* DROP означає: повідомлення наше — нам і звільняти */
  return GST_BUS_DROP;
}

/* поруч із gst_bus_add_watch(), до першого set_state */
gst_bus_set_sync_handler (app.bus, on_sync_message, NULL, NULL);
```
```py
gi.require_version("GstVideo", "1.0")
from gi.repository import GstVideo

def on_sync_message(bus, msg, handle):
    if not GstVideo.is_video_overlay_prepare_window_handle_message(msg):
        return Gst.BusSyncReply.PASS      # решта — звичайним шляхом, у чергу

    msg.src.set_window_handle(handle)     # unref тут не потрібен: його робить зв'язувач
    return Gst.BusSyncReply.DROP

# поруч із add_watch(), до першого set_state
bus.set_sync_handler(on_sync_message, window_handle)
```
:::

Три правила для такого обробника. Він мусить бути коротким — доки він працює, нитка потоку стоїть. Він не має права ходити у віджети — він **не** в головній нитці. І він не має права питати конвеєр про стан чи міняти його — це прохання до нитки зачекати на саму себе. Усе, що не стосується вікна, він відпускає з `GST_BUS_PASS`, і воно доходить до звичайного обробника як завжди.

## Чиста зупинка

![Порядок кроків програми: стеження приєднати до першого set_state, конвеєр вимкнути до зняття стеження](/reference/media-vision/gstreamer/bus-and-messages/img/proj-run-order.svg)

*Порядок кроків: кожен на своєму місці не з естетики — переставлені місцями, вони дають або втрачені повідомлення, або звернення до звільненої пам'яті.*

Вихід у цій програмі один — і після `EOS`, і після `ERROR` керування повертається з `g_main_loop_run()` в те саме місце. Це навмисно: два різні шляхи виходу означали б два різні набори звільнень, і один із них рано чи пізно виявився б неповним. Такий єдиний шлях згортання — те саме, що загальне [штатне вимкнення](book:programming/graceful-shutdown), тільки в мініатюрі.

Порядок кроків у ньому не довільний.

`set_state(NULL)` **перший**, бо доти нитки потоку ще працюють, і розбирати з-під них щось — гарантована аварія. Цей перехід синхронний: коли виклик повернувся, усередині вже нічого не рухається й ресурси віддано.

Одразу з цим переходом конвеєр **скидає шину**: усе, що в черзі, викидається, усе нове відхиляється. Це навмисне — під час розбирання елементи ще встигають напостити купу вже нікому не потрібного. Побічний ефект: після цього рядка з шини не прочитати нічого. Якщо останні повідомлення вам таки потрібні, вимкніть властивість конвеєра `auto-flush-bus` — і тоді скидати шину стане вашим обов'язком, інакше повідомлення від попереднього пуску прилетять під час наступного.

`gst_bus_remove_watch()` **другий**, до `unref` шини: стеження — це джерело подій у головному циклі, яке тримає власне посилання на шину. Не знявши його, ви лишаєте в циклі джерело, що вказує на об'єкт, який ви щойно збиралися звільнити.

І тільки після цього — `unref` шини, `unref` конвеєра (він потягне за собою всі елементи всередині), `unref` циклу.

## Три пастки, на яких програма мовчить

Усі три виглядають однаково — конвеєр начебто працює, а програма не реагує ні на що, — і всі три видає один рядок у журналі, той, що починається словами «queue overflows with». Він з'являється, коли довжина черги перетинає 1024, і потім на кожній наступній тисячі. Пишеться на рівні попереджень, тобто видно його вже за `GST_DEBUG=2`; за типового мовчазного налаштування — не видно взагалі, і саме тому пам'ять «росте без причини».

**Стеження не приєднано.** Конвеєр створено, `set_state` викликано, `gst_bus_add_watch()` забуто — або викликано вдруге. Шина тримає рівно **одне** стеження, і другий виклик поверне 0, нічого не приєднавши; те саме стосується пари `add_watch` і `add_signal_watch` разом. Перевірка на нуль тут — рядок, який економить годину.

**Головний цикл ніхто не крутить.** Стеження приєднується до типового головного контексту GLib, і якщо в застосунку свій цикл подій — чужого набору віджетів, власного сервера, чого завгодно, — цей контекст не обертається ніколи. Виходів два. Перший: підняти `GMainLoop` в окремій нитці. Другий, простіший: не приєднувати стеження взагалі, а вичерпувати шину з таймера свого циклу — і тоді власником повідомлень стаєте ви:

```c
/* «стеження» вручну: кликати з таймера чужого циклу, скажімо раз на 50 мс.
   gst_bus_add_watch() у цьому варіанті НЕ викликати — стеження одне на шину. */
static void pump_bus (App *app)
{
  GstMessage *msg;
  while ((msg = gst_bus_pop (app->bus)) != NULL) {
    on_bus_message (app->bus, msg, app);   /* та сама функція, що й у стеженні */
    gst_message_unref (msg);               /* але звільняємо ТЕПЕР ми */
  }
}
```

**Обробник працює довго.** Цикл є, крутиться, обробник викликається — але всередині нього похід у мережу, запис у базу або перемальовування всього інтерфейсу. Повідомлення надходять швидше, ніж ви їх розбираєте, і черга росте. Найшвидше її набивають `QOS` і `STATE_CHANGED`: на живому відео це десятки повідомлень за секунду. Правило просте — усе, що триває довше за мить, кладеться у власну чергу задач і виконується поза обробником. Спіймати порушення можна дешево:

```c
    gint64 t0 = g_get_monotonic_time ();
    /* … тіло switch … */
    gint64 dt = g_get_monotonic_time () - t0;
    if (dt > 2000)     /* понад 2 мс у колбеку шини — вже погано */
      g_warning ("обробник шини витратив %" G_GINT64_FORMAT " мкс на %s",
                 dt, GST_MESSAGE_TYPE_NAME (msg));
```

Спільне в цих трьох пастках одне, і воно ж — головна думка всієї програми: шина нічого не робить сама. Вона доповідає факт і чекає, доки хтось його забере й вирішить, що з ним робити. Конвеєр, у якому ніхто не забирає, працює бездоганно й безглуздо.

## Що це коштує і чого тут немає

Ціна всієї конструкції — одна нитка (та, що крутить цикл), одне виділення пам'яті на повідомлення й приблизно нуль накладних витрат на кадр: шина в дорозі даних не стоїть узагалі. Обробник із десятком гілок `switch` при десятках повідомлень на секунду не помітний на тлі декодування навіть на слабкому процесорі — за умови, що в ньому справді нічого довгого.

Чого тут навмисно немає: перемотування (воно тягне за собою розчистку конвеєра й окрему обробку `ASYNC_DONE`), перебудови конвеєра на льоту й видачі кадрів у власний код. Останнє додається дешевше за все — заміною `autovideosink` на [appsink](book:media-vision/appsink-appsrc), після чого весь наведений код лишається без жодної зміни, а кадри починають приходити у ваш колбек. Коли ж програма поводиться незрозуміло попри правильно оброблену шину, наступний інструмент — граф конвеєра й рівні журналу, про які йдеться в статті про [діагностику конвеєра](book:media-vision/pipeline-debugging).
