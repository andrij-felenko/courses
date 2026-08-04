# ⚙️ Надрукувати мапу ниток: проба на кожному паді

Двісті рядків мовою C, які на будь-якому конвеєрі відповідають на питання «скільки тут ниток і де саме межа» не здогадом за виглядом рядка, а виміром: програма чіпляє пробу на кожен пад кожного елемента й на першому ж буфері друкує ім'я елемента, ім'я пада та нитку, у якій це сталося. З готової таблиці межа читається очима. Другим прогоном та сама програма прибирає черги з гілок і показує, як конвеєр не доїжджає до `PAUSED`, — разом із трьома способами побачити, хто на кого чекає.

Мова тут не з вибору. Проби, задачі й пул ниток — це API самої бібліотеки, написаної мовою C поверх GObject; обгортки для інших мов переносять ті самі виклики, не міняючи ні порядку, ні змісту.

## Чому мапу не можна вивести з опису

Спокуса порахувати нитки в голові велика: подивився на рядок, полічив `queue`, додав одиницю за джерело. На простому ланцюзі це навіть спрацює — і саме тому потім боляче.

Наочних пасток тут три. Перша: `autovideosink` — не елемент, а бін, який у `READY` підбирає собі справжній стік і ховає його всередині; що там усередині й скільки в нього падів, з рядка не видно взагалі. Друга: чимало елементів заводять власні нитки поза моделлю падів — декодер бере стільки робітників, скільки в машині ядер, `rtspsrc` розгортає всередині цілий вузол зі своїми задачами. Третя: пади бувають запитувані й динамічні, тож набір падів у момент складання конвеєра й набір падів через секунду роботи — це різні набори.

Тому єдиний чесний спосіб — спитати сам конвеєр, коли він уже працює. Питання ставиться пробою: функцією, яку бібліотека покличе просто посеред передачі буфера, у тій самій нитці, що цей буфер несе. Проба не змінює нічого; вона лише дивиться, де опинилася.

## Що тримає програма

```c
/* thread-map.c — друкує справжню мапу ниток конвеєра GStreamer.
 *
 * збірка:
 *   cc thread-map.c -o thread-map $(pkg-config --cflags --libs gstreamer-1.0)
 * запуск:
 *   ./thread-map              # із чергами на гілках — працює
 *   ./thread-map --no-queue   # без черг — конвеєр не доїде до PAUSED
 */
#include <gst/gst.h>

typedef struct {
  GThread *thread;   /* нитка, у якій спрацювала проба */
  gint     tid;      /* наш короткий номер: T1, T2, … */
  gchar   *elem;     /* ім'я елемента */
  gchar   *pad;      /* ім'я пада */
  gchar    dir;      /* '<' вхідний, '>' вихідний */
} Mark;

static GMutex      log_lock;   /* один замок на друк і на обидві таблиці */
static GArray     *marks;      /* Mark у порядку появи */
static GHashTable *tids;       /* GThread* → номер нитки */
static GThread    *thr[64];    /* номер нитки → GThread* */
static gint        next_tid = 1;

/* Короткий номер нитки. Викликати з узятим log_lock. */
static gint
thread_number (GThread *t)
{
  gpointer v = g_hash_table_lookup (tids, t);

  if (v == NULL && next_tid < (gint) G_N_ELEMENTS (thr)) {
    v = GINT_TO_POINTER (next_tid);
    thr[next_tid++] = t;
    g_hash_table_insert (tids, t, v);
  }
  return GPOINTER_TO_INT (v);
}
```

Найважливіше тут — короткий номер. `GThread *` цілком годиться, щоб розрізняти нитки, але вісім шістнадцяткових цифр у кожному рядку перетворюють вивід на шифр, який доводиться розгадувати замість читати. Тому кожна нова нитка дістає порядковий номер при першій же появі, а вказівник друкується один раз у підсумку.

Побічний наслідок цього рішення виявиться корисним: номер `T1` дістанеться тій нитці, яка звернеться першою, — а першою звернеться нитка застосунку, ще до будь-яких даних. Далі буде видно, що біля `T1` у мапі не з'явиться жодного пада, і це не збій, а найкоротший доказ того, що нитка застосунку й нитки потоку — різні речі.

## Проба: один буфер, один рядок, і відразу геть

```c
/* Спрацьовує на ПЕРШОМУ буфері цього пада й одразу знімає себе.
   Виконується в нитці потоку, із узятим замком потоку — тому тут
   дозволено рівно два рухи: узяти імена й надрукувати рядок. */
static GstPadProbeReturn
first_buffer (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  GstElement *owner = gst_pad_get_parent_element (pad);
  Mark m;

  m.thread = g_thread_self ();
  m.elem   = owner ? gst_element_get_name (owner) : g_strdup ("?");
  m.pad    = gst_pad_get_name (pad);
  m.dir    = (GST_PAD_DIRECTION (pad) == GST_PAD_SINK) ? '<' : '>';

  g_mutex_lock (&log_lock);
  m.tid = thread_number (m.thread);
  g_array_append_val (marks, m);
  g_print ("  T%-2d  %-34s %c %s\n", m.tid, m.elem, m.dir, m.pad);
  g_mutex_unlock (&log_lock);

  if (owner)
    gst_object_unref (owner);

  return GST_PAD_PROBE_REMOVE;   /* нас цікавив ЛИШЕ перший буфер */
}
```

Три рядки цієї функції варті окремого погляду.

`g_thread_self ()` — уся суть виміру. Проба не отримує нитку параметром і не питає її в конвеєра: вона просто дивиться, у чиєму стеку виконується. Відповідь правдива за побудовою, бо іншої нитки, ніж та, у якій ти зараз працюєш, тут узнати неможливо.

`GST_PAD_PROBE_REMOVE` знімає пробу відразу після першого спрацювання. Це не економія заради економії: проба лишається в списку хуків пада й перевіряється на кожному буфері, а друк із неї серіалізує всі нитки на одному замку `stdout`. Знята проба коштує рівно стільки, скільки не встановлена, — нуль.

Замок `log_lock` тут не для краси. Проби спрацьовують у кількох нитках одночасно, а `g_print` без спільного замка перемішає половини рядків; та й нумерація ниток — це читання-запис по спільній хеш-таблиці.

![Стек однієї передачі буфера: цикл задачі, gst_pad_push, проба на вихідному паді, gst_pad_chain_data із узятим замком потоку, проба на вхідному паді, chain() наступного елемента](/reference/media-vision/gstreamer/threads-and-queues/img/probe-in-stack.svg)

*Проба — не окремий механізм спостереження, а звичайний кадр чужого стеку, під яким уже лежить чужий замок.*

Із цієї картинки випливає єдине правило користування пробами, і воно жорсткіше, ніж здається: проба виконується в нитці потоку, і в її стеку вже взято щонайменше один замок потоку — того пада, чия задача веде цю нитку; для проби на вхідному паді взято ще й замок самого цього пада, бо його бере `gst_pad_chain_data` перед викликом хуків. Усе, що всередині проби чекає, зупиняє не пробу, а весь ланцюг над нею.

## Обхід падів: GstIterator і чому саме в READY

```c
/* Повісити пробу на кожен пад одного елемента. Самого BUFFER мало:
   елемент може штовхати списки буферів, і тоді проба на самі лише
   буфери просто мовчить. */
static void
probe_pads (GstElement *elem)
{
  GstIterator *it = gst_element_iterate_pads (elem);
  GValue item = G_VALUE_INIT;
  gboolean done = FALSE;

  while (!done) {
    switch (gst_iterator_next (it, &item)) {
      case GST_ITERATOR_OK:
        gst_pad_add_probe (GST_PAD (g_value_get_object (&item)),
                           GST_PAD_PROBE_TYPE_BUFFER |
                           GST_PAD_PROBE_TYPE_BUFFER_LIST,
                           first_buffer, NULL, NULL);
        g_value_reset (&item);      /* GValue тримав посилання — віддаємо */
        break;
      case GST_ITERATOR_RESYNC:     /* список падів змінився під нами */
        gst_iterator_resync (it);   /* обхід починається спочатку */
        break;
      default:                      /* DONE або ERROR */
        done = TRUE;
        break;
    }
  }
  g_value_unset (&item);
  gst_iterator_free (it);
}

/* Те саме по всіх елементах конвеєра, разом із тими, що лежать усередині
   вкладених бінів: autovideosink — саме такий бін. */
static void
for_each_element (GstElement *pipeline, void (*fn) (GstElement *))
{
  GstIterator *it = gst_bin_iterate_recurse (GST_BIN (pipeline));
  GValue item = G_VALUE_INIT;
  gboolean done = FALSE;

  while (!done) {
    switch (gst_iterator_next (it, &item)) {
      case GST_ITERATOR_OK:
        fn (GST_ELEMENT (g_value_get_object (&item)));
        g_value_reset (&item);
        break;
      case GST_ITERATOR_RESYNC:
        gst_iterator_resync (it);
        break;
      default:
        done = TRUE;
        break;
    }
  }
  g_value_unset (&item);
  gst_iterator_free (it);
}
```

Ітератор бібліотеки має форму, яка спершу дратує, а потім виявляється чесною: він може відповісти `RESYNC` — «список під тобою змінився, почни спочатку». Це не дефект, а зізнання: пади з'являються й зникають у нитках потоку, і жоден знімок списку не буває дійсним довго. Гілка `RESYNC`, дописана «щоб компілятор мовчав», — найкоротший шлях до обходу, який мовчки пропускає половину падів під час динамічного під'єднання.

Момент обходу вибрано не навмання. У `NULL` `autovideosink` ще не знає, яким стоком він буде, і його нутрощів не існує. У `PAUSED` уже пройшов префрол, тобто перший буфер кожного стоку вже проїхав — і саме його ми хотіли зловити. Лишається вузьке вікно `READY`: усі елементи на місці, усі пади створені, даних ще нема жодного.

## Хто створює нитки: STREAM_STATUS у своїй нитці

```c
/* Синхронний обробник шини: виконується в нитці ТОГО, ХТО ПОСТИТЬ
   повідомлення. Саме тому тут видно різницю між тим, хто задачу
   створює, і тим, хто в неї входить. */
static GstBusSyncReply
on_message_sync (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  if (GST_MESSAGE_TYPE (msg) == GST_MESSAGE_STREAM_STATUS) {
    GstStreamStatusType type;
    GstElement *owner = NULL;
    const GValue *val;
    GstTask *task = NULL;
    const gchar *word = NULL;

    gst_message_parse_stream_status (msg, &type, &owner);
    val = gst_message_get_stream_status_object (msg);
    if (val != NULL && G_VALUE_TYPE (val) == GST_TYPE_TASK)
      task = g_value_get_object (val);

    switch (type) {
      case GST_STREAM_STATUS_TYPE_CREATE:
        word = "CREATE";
        /* ЄДИНИЙ момент, коли можна підсунути власний пул ниток:
             gst_task_set_pool (task, my_pool);
           після повернення звідси задача вже візьме типовий. */
        break;
      case GST_STREAM_STATUS_TYPE_ENTER:
        word = "ENTER";
        /* ми вже ВСЕРЕДИНІ нової нитки — тут виставляють пріоритет:
             struct sched_param p = { .sched_priority = 10 };
             pthread_setschedparam (pthread_self (), SCHED_RR, &p); */
        break;
      case GST_STREAM_STATUS_TYPE_LEAVE:
        word = "LEAVE";
        break;
      default:
        break;
    }

    if (word != NULL) {
      g_mutex_lock (&log_lock);
      g_print ("  [%-6s] задача «%s» від «%s» — ми зараз у T%d\n", word,
               task  ? GST_OBJECT_NAME (task)  : "?",
               owner ? GST_OBJECT_NAME (owner) : "?",
               thread_number (g_thread_self ()));
      g_mutex_unlock (&log_lock);
    }
  }
  return GST_BUS_PASS;   /* нічого не ковтаємо: далі повідомлення йде як завжди */
}
```

Обробник саме синхронний, і слово це тут технічне: він виконується просто в тій нитці, яка поклала повідомлення, до того як керування повернеться. Звичайний обробник [шини повідомлень](book:media-vision/bus-and-messages) забирає повідомлення пізніше й із головного циклу — для `CREATE` це запізно, бо задача вже стартувала б із типовим пулом, а для `ENTER` просто безглуздо, бо весь сенс цього повідомлення в тому, у якій нитці воно приходить.

Різниця між трьома словами читається прямо з виводу. `CREATE` приходить у нитці того, хто задачу заводить, — і це буде нитка застосунку, що змінює стан. `ENTER` і `LEAVE` приходять уже зсередини нової нитки, на її вході й виході. Тому `ENTER` — єдине місце, де політику планувальника задають тій нитці, якій вона призначена, а не сусідній; що при цьому насправді відбувається в ядрі й чому `SCHED_RR` без відповідного дозволу просто не встановиться, — у темі [пріоритети, nice і реальночасові класи](book:unix-linux/priority-nice-realtime).

`GST_BUS_PASS` наприкінці обов'язковий. Синхронний обробник має право проковтнути повідомлення, повернувши `GST_BUS_DROP`, — і тоді помилки й `EOS` не дійдуть до застосунку взагалі.

## Головна частина

```c
static void
dump_one_state (GstElement *e)
{
  GstState cur, pending;

  gst_element_get_state (e, &cur, &pending, 0);
  g_print ("  %-36s %-8s → %-12s%s\n", GST_OBJECT_NAME (e),
           gst_element_state_get_name (cur),
           gst_element_state_get_name (pending),
           pending != GST_STATE_VOID_PENDING ? "  ← ось хто не доїхав" : "");
}

static void
print_map (void)
{
  gint t;
  guint i;

  g_mutex_lock (&log_lock);
  g_print ("\n=== мапа ниток: %u падів у %d нитках ===\n", marks->len, next_tid - 1);
  for (t = 1; t < next_tid; t++) {
    guint own = 0;

    g_print ("\nT%d  (%p)\n", t, (void *) thr[t]);
    for (i = 0; i < marks->len; i++) {
      Mark *m = &g_array_index (marks, Mark, i);

      if (m->tid != t)
        continue;
      g_print ("    %-36s %c %s\n", m->elem, m->dir, m->pad);
      own++;
    }
    if (own == 0)
      g_print ("    (жодного пада — через цю нитку дані не течуть)\n");
  }
  g_mutex_unlock (&log_lock);
}

int
main (int argc, char *argv[])
{
  const gchar *with_queue =
      "videotestsrc num-buffers=300 ! tee name=t "
      "t. ! queue ! autovideosink "
      "t. ! queue ! jpegenc ! fakesink";
  const gchar *no_queue =
      "videotestsrc num-buffers=300 ! tee name=t "
      "t. ! autovideosink "
      "t. ! jpegenc ! fakesink";
  gboolean bare = (argc > 1 && g_strcmp0 (argv[1], "--no-queue") == 0);
  GError *err = NULL;
  GstElement *pipeline;
  GstBus *bus;
  GstStateChangeReturn ret;
  guint i;

  gst_init (&argc, &argv);
  g_mutex_init (&log_lock);
  marks = g_array_new (FALSE, FALSE, sizeof (Mark));
  tids  = g_hash_table_new (NULL, NULL);

  pipeline = gst_parse_launch (bare ? no_queue : with_queue, &err);
  if (pipeline == NULL) {
    g_printerr ("конвеєр не зібрався: %s\n", err->message);
    return 1;
  }

  bus = gst_element_get_bus (pipeline);
  gst_bus_set_sync_handler (bus, on_message_sync, NULL, NULL);

  g_mutex_lock (&log_lock);
  g_print ("нитка застосунку: T%d (%p)\n\n",
           thread_number (g_thread_self ()), (void *) g_thread_self ());
  g_mutex_unlock (&log_lock);

  /* READY, а не одразу PAUSED: у READY autovideosink уже обрав справжній
     стік і має всі пади, але жодного буфера ще не було. */
  if (gst_element_set_state (pipeline, GST_STATE_READY) == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("не піднявся навіть у READY\n");
    return 1;
  }
  for_each_element (pipeline, probe_pads);

  gst_element_set_state (pipeline, GST_STATE_PLAYING);

  /* Чекаємо з обмеженням, а не назавжди: різницю між робочим конвеєром
     і зависанням видно саме тут. */
  ret = gst_element_get_state (pipeline, NULL, NULL, 5 * GST_SECOND);
  if (ret == GST_STATE_CHANGE_ASYNC) {
    g_print ("\n!! за 5 с конвеєр не дійшов до PLAYING. Стани елементів:\n");
    dump_one_state (pipeline);
    for_each_element (pipeline, dump_one_state);
  } else {
    g_usleep (500 * 1000);
    print_map ();
  }

  gst_element_set_state (pipeline, GST_STATE_NULL);

  for (i = 0; i < marks->len; i++) {
    Mark *m = &g_array_index (marks, Mark, i);
    g_free (m->elem);
    g_free (m->pad);
  }
  g_array_free (marks, TRUE);
  g_hash_table_destroy (tids);
  gst_object_unref (bus);
  gst_object_unref (pipeline);
  return 0;
}
```

Обмежене очікування замість вічного — головне рішення цієї функції. `gst_element_get_state` з `GST_CLOCK_TIME_NONE` на зіпсованому конвеєрі просто не повертається, і програма перетворюється на об'єкт для налагоджувача. З п'ятисекундною межею вона натомість сама доповідає, що перехід не завершився, і тут же друкує стани всіх елементів — тобто перетворює зависання на діагноз. Що означають ці стани й чому стік доповідає про готовність із затримкою, розібрано в темі [стани конвеєра](book:media-vision/states-lifecycle).

## Мапа, яку друкує програма

```
$ ./thread-map
нитка застосунку: T1 (0x55c4f1a2b2a0)

  [CREATE] задача «queue1:src» від «queue1» — ми зараз у T1
  [ENTER ] задача «queue1:src» від «queue1» — ми зараз у T2
  [CREATE] задача «queue0:src» від «queue0» — ми зараз у T1
  [ENTER ] задача «queue0:src» від «queue0» — ми зараз у T3
  [CREATE] задача «videotestsrc0:src» від «videotestsrc0» — ми зараз у T1
  [ENTER ] задача «videotestsrc0:src» від «videotestsrc0» — ми зараз у T4
  T4   videotestsrc0                        > src
  T4   tee0                                 < sink
  T4   tee0                                 > src_0
  T4   queue0                               < sink
  T4   tee0                                 > src_1
  T4   queue1                               < sink
  T3   queue0                               > src
  T2   queue1                               > src
  T3   autovideosink0                       < sink
  T2   jpegenc0                             < sink
  T3   autovideosink0-actual-sink-xvimage   < sink
  T2   jpegenc0                             > src
  T2   fakesink0                            < sink

=== мапа ниток: 13 падів у 4 нитках ===

T1  (0x55c4f1a2b2a0)
    (жодного пада — через цю нитку дані не течуть)

T2  (0x7f2b3c0021d0)
    queue1                               > src
    jpegenc0                             < sink
    jpegenc0                             > src
    fakesink0                            < sink

T3  (0x7f2b340020a0)
    queue0                               > src
    autovideosink0                       < sink
    autovideosink0-actual-sink-xvimage   < sink

T4  (0x7f2b2c002100)
    videotestsrc0                        > src
    tee0                                 < sink
    tee0                                 > src_0
    queue0                               < sink
    tee0                                 > src_1
    queue1                               < sink
```

Читається ця таблиця буквально за десять секунд, і кожен рядок каже щось конкретне.

**Межа проходить усередині черги, а не між елементами.** `queue0 < sink` стоїть у `T4`, `queue0 > src` — у `T3`. Той самий елемент, дві різні нитки; лінія розрізу проходить крізь нього.

**`tee` нитки не додає.** Усі три його пади в `T4`, разом із джерелом. Він роздає буфер гілкам послідовно, тією самою ниткою, і його вихідні пади — це просто місце, звідки робиться наступний виклик. Уся паралельність гілок з'являється лише в чергах за ним.

**Фільтр не додає нитки й поготів.** `jpegenc0 < sink` і `jpegenc0 > src` в одній нитці `T2`, між ними немає нічого — стиснення кадру відбувається просто в стеку того, хто приніс буфер.

**Гост-пад нитки не міняє.** `autovideosink0 < sink` і `autovideosink0-actual-sink-xvimage < sink` обидва в `T3`: зовнішній пад біна лише пересилає буфер на внутрішній пад справжнього стоку, і це знову звичайний виклик.

**У нитці застосунку немає жодного пада.** `T1` створила конвеєр, поставила стани, отримала три повідомлення `CREATE` — і не понесла жодного буфера. Обробники, які застосунок вішає на елементи, виконуються не тут.

> 🔧 **Навіщо це.** Мапа потрібна не для цікавості, а для перевірки чужої роботи. Топологію, успадковану разом із проєктом, зазвичай супроводжує усна легенда — «тут у нас декодування в окремій нитці». Прогін цієї програми за хвилину або підтверджує легенду, або показує, що всі шість елементів сидять в одній нитці, а `queue` стоїть на гілці, якою за весь час не пройшло жодного буфера. Ті самі тринадцять рядків годяться й на приймальну перевірку: якщо після правки топології мапа змінилася, а ніхто цього не планував, правка зачепила більше, ніж думав автор.

## Другий прогін: прибрати черги й подивитися, хто на кого чекає

```
$ ./thread-map --no-queue
нитка застосунку: T1 (0x561e0c8ab2a0)

  [CREATE] задача «videotestsrc0:src» від «videotestsrc0» — ми зараз у T1
  [ENTER ] задача «videotestsrc0:src» від «videotestsrc0» — ми зараз у T2
  T2   videotestsrc0                        > src
  T2   tee0                                 < sink
  T2   tee0                                 > src_0
  T2   autovideosink0                       < sink
  T2   autovideosink0-actual-sink-xvimage   < sink

!! за 5 с конвеєр не дійшов до PLAYING. Стани елементів:
  pipeline0                            READY    → PLAYING       ← ось хто не доїхав
  fakesink0                            READY    → PAUSED        ← ось хто не доїхав
  jpegenc0                             PAUSED   → VOID_PENDING
  autovideosink0                       PAUSED   → VOID_PENDING
  autovideosink0-actual-sink-xvimage   PAUSED   → VOID_PENDING
  tee0                                 PAUSED   → VOID_PENDING
  videotestsrc0                        PAUSED   → VOID_PENDING
```

Вивід уривається на п'ятому рядку — і місце обриву й є діагнозом. Проби на `tee0 > src_1`, на `jpegenc0` і на `fakesink0` не спрацювали жодного разу: у другу гілку не зайшов жоден буфер. Разом із таблицею станів це вже повна картина. Усі елементи доїхали до `PAUSED`, крім `fakesink0`, який лишився в `READY` і винен `PAUSED`; `jpegenc0` при цьому в `PAUSED`, бо перетворювачам для переходу дані не потрібні, а стокові — потрібні.

Далі коло замикається саме собою. `tee` віддав перший буфер у першу гілку; стік узяв його на префрол і заснув до `PLAYING`, не повернувшись із функції обробки; отже, `tee` не дійшов до другої гілки; отже, `fakesink0` не отримав буфера й не префролив; отже, `PAUSED` для конвеєра не завершився; отже, `PLAYING` не настане й перший стік не прокинеться. Це [дедлок](book:programming/deadlock) без жодного явного замка — просто чотири очікування, замкнені в кільце.

Два незалежні підтвердження, які варто вміти брати, коли таблиці станів мало.

**Журнал переходів.** Категорія `GST_STATES` друкує рядок про завершення переходу для кожного елемента окремо:

```sh
GST_DEBUG=GST_STATES:5 ./thread-map --no-queue 2>&1 \
  | grep -E 'completed state change|fakesink0'
```

Рядок «completed state change to PAUSED» знайдеться для всіх, крім `fakesink0`, — а для нього останнє, що є в журналі, це початок переходу, який лишився асинхронним. Заразом варто перед виходом покласти знімок графа: `GST_DEBUG_BIN_TO_DOT_FILE_WITH_TS (GST_BIN (pipeline), GST_DEBUG_GRAPH_SHOW_ALL, "hang")` за виставленої змінної `GST_DEBUG_DUMP_DOT_DIR` малює конвеєр разом зі станами й caps кожного пада; про решту важелів журналу — у темі [діагностика конвеєра](book:media-vision/pipeline-debugging).

**Стеки всіх ниток.** Замініть у програмі `5 * GST_SECOND` на `GST_CLOCK_TIME_NONE`, щоб було коли під'єднатися, і подивіться на процес налагоджувачем — механіку такого під'єднання розібрано в темі [ptrace](book:unix-linux/ptrace-model):

```
$ gdb -p $(pidof thread-map)
(gdb) thread apply all bt
```

```
Thread 1 "thread-map"          ← нитка застосунку
#0  g_cond_wait_until
#1  gst_element_get_state_func      чекає на завершення переходу
#2  main

Thread 4 "videotestsrc0:s"     ← задача джерела; ім'я Linux обрізає до 15 літер
#0  g_cond_wait
#1  gst_base_sink_wait_preroll      стік узяв буфер і спить до PLAYING
#2  gst_base_sink_chain_unlocked
#3  gst_base_sink_chain
#4  gst_pad_push                    сюди його загнав tee
#5  gst_tee_handle_data
#6  gst_pad_push
#7  gst_base_src_loop
#8  gst_task_func
```

*(Кадри скорочено, назви функцій між версіями трохи різняться.)*

Одна нитка тут несе весь ланцюг від джерела до стоку — це видно просто з того, що `gst_base_src_loop` і `gst_base_sink_chain` лежать в одному стеку. Заразом видно, що імена ниток не треба вигадувати: задача сама виставляє собі за ім'я нитки ім'я свого об'єкта, тож `thread apply all bt` одразу підписаний назвами падів.

Поверніть `queue` на обидві гілки — і той самий бінарник друкує повну мапу з чотирьох ниток. Змінилося рівно те, що функція обробки черги нікого не чекає: узяла буфер, розбудила власну нитку, повернулася, — і `tee` встиг дійти до другої гілки.

## Зупинити конвеєр із проби

Наступне, чого хочеться від проби після мапи, — щоб вона щось вирішувала: скажімо, гасила конвеєр після сотого кадру. Наївний варіант із `gst_element_set_state (pipeline, GST_STATE_NULL)` прямо в пробі вішає програму намертво, і причина вже названа: перехід у `NULL` зобов'язаний дочекатися виходу всіх ниток потоку, а одна з них — саме та, що стоїть у цій пробі й чекає на повернення з `set_state`.

```c
/* Виконується вже в чужій нитці з пулу — тут можна все. */
static void
stop_now (GstElement *pipeline, gpointer user_data)
{
  gst_element_send_event (pipeline, gst_event_new_eos ());
}

/* А ця проба лишається на паді й рахує кадри. */
static GstPadProbeReturn
count_frames (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  static gint n = 0;

  if (g_atomic_int_add (&n, 1) == 99)
    gst_element_call_async (GST_ELEMENT (user_data), stop_now, NULL, NULL);

  return GST_PAD_PROBE_OK;
}
```

`gst_element_call_async` бере нитку з внутрішнього пулу й виконує зворотний виклик поза потоком; сама проба при цьому повертається негайно й замка не тримає. У версіях від 1.28 ця функція перейменована на `gst_object_call_async`, стара лишилася застарілим синонімом.

`EOS` замість `set_state (NULL)` тут не дрібниця: подія проходить конвеєром від джерел униз, стоки дописують те, що мали дописати, і застосунок дізнається про кінець із шини — тобто зупинка виходить упорядкованою, а не обірваною посеред кадру.

## Скільки це коштує і де ламається

Обхід — `O(E · P)` за кількістю елементів і падів, і робиться один раз у `READY`; на цьому конвеєрі це вісім елементів і тринадцять падів, тобто мікросекунди. Уся ціна програми — в іншому місці.

**Скільки коштує забути `GST_PAD_PROBE_REMOVE`.**

```
восьмикамерна система, проби лишилися ввімкненими:
  8 камер · 30 кадрів/с · 13 падів = 3120 викликів проби за секунду

кожен виклик:  обхід списку хуків пада + друк
друк:          усі 3120 через ОДИН замок stdout
```

Три тисячі викликів за секунду самі по собі дрібниця; смертельний тут замок `stdout`, на якому шістнадцять ниток потоку шикуються в чергу. Вимір, який спотворює вимірюване, — найгірший вид виміру, тому проба знімає себе першим же буфером.

Далі — те, що ламається в такій програмі найчастіше.

**Тільки `BUFFER` — проба мовчить.** Елемент має право штовхати не буфер, а список буферів, і проба, зареєстрована самим лише `GST_PAD_PROBE_TYPE_BUFFER`, у цьому разі не викликається. Пад виглядає як «мертвий», хоч даних через нього течуть мегабайти. Реєструйте `GST_PAD_PROBE_TYPE_BUFFER | GST_PAD_PROBE_TYPE_BUFFER_LIST` завжди, коли просто спостерігаєте.

**`RESYNC` чіпляє пробу двічі.** Після повторної синхронізації обхід починається спочатку, і пади, які вже отримали пробу, отримають другу. У `READY` список стабільний, тож тут це не спрацює, — але для обходу живого конвеєра тримайте множину вже оброблених падів і звіряйтеся з нею.

**Пади, яких ще нема.** Обхід бачить лише те, що існує в момент виклику: запитувані пади `tee`, динамічні пади розбирача, гілки, які добере автодобір, з'являться пізніше. Щоб не проґавити їх, слухайте сигнал `pad-added` на елементі й `deep-element-added` на конвеєрі — і чіпляйте пробу з обробника, пам'ятаючи, що виконується він у нитці потоку.

**Номери ниток — наші, не системні.** `T2` цієї програми не має нічого спільного з ідентифікатором нитки в `top` чи в налагоджувачі; це просто порядок першої появи, і при наступному запуску він може бути іншим. Спільне ім'я, за яким мапа зшивається з `thread apply all bt`, — це ім'я задачі на кшталт `queue0:src`, обрізане в Linux до п'ятнадцяти літер.

**Нитки повертаються в пул.** Задача не володіє ниткою: зупинившись, вона віддає її назад, і наступна задача може отримати ту саму. Отже, `GThread *` однозначний лише поки конвеєр не міняв стану; мапа правдива для одного прогону, а не назавжди.

**Синхронний обробник — теж чужа нитка.** Усе сказане про проби діє й тут: `on_message_sync` виконується в нитці того, хто поклав повідомлення. Важкий розбір або, тим паче, зміна стану звідти дає ті самі зависання, тільки шукати їх довше, бо код виглядає як звичайний обробник подій.
