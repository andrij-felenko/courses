/* syncplay.c — синхронний показ на кількох машинах:
 *   спільний годинник (GstNetTimeProvider ⇄ GstNetClientClock)
 *   плюс спільний base_time, роздати який доводиться самотужки.
 *
 * збірка:
 *   gcc -O2 -Wall syncplay.c -o syncplay \
 *       $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-net-1.0 gio-2.0)
 *
 * запуск (спершу майстер):
 *   A$ ./syncplay master 1                 # чекає на одного підлеглого
 *   B$ ./syncplay slave 192.168.1.10
 */
#include <gst/gst.h>
#include <gst/net/gstnet.h>
#include <gio/gio.h>
#include <stdlib.h>
#include <string.h>

#define CLOCK_PORT    5637            /* UDP: час; типовий порт GstNetTimeProvider */
#define BASE_PORT     5638            /* TCP: роздача base_time                    */
#define START_DELAY   (GST_SECOND)    /* запас між роздачею T і самим T            */
#define SYNC_TIMEOUT  (30 * GST_SECOND)

/* М'яч рухається як функція running_time, тому вміст кадру визначений
   однозначно на будь-якій машині — спільний файл для проби не потрібен. */
static const gchar *PIPELINE_DESC =
  "videotestsrc pattern=ball animation-mode=running-time is-live=false ! "
  "video/x-raw,width=1280,height=720,framerate=60/1 ! "
  "timeoverlay time-mode=running-time font-desc=\"Sans 40\" ! tee name=t "
  "t. ! queue ! videoconvert ! autovideosink name=screen "
  "t. ! queue ! fakesink name=probe sync=true signal-handoffs=true";

typedef struct {
  GstElement *pipeline;
  GstClock   *clock;
  GMainLoop  *loop;
  GList      *pending;   /* GSocketConnection*: підлеглі, що вже синхронні, чекають T */
  guint       want;      /* скільки підлеглих зібрати перед стартом (майстер)        */
} App;
