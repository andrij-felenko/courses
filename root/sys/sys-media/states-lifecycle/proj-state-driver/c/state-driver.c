/* state-driver.c — керований життєвий цикл конвеєра GStreamer.
 *
 * збірка:
 *   cc state-driver.c -o state-driver $(pkg-config --cflags --libs gstreamer-1.0)
 * файл:
 *   ./state-driver "filesrc location=clip.mp4 ! decodebin ! videoconvert ! autovideosink"
 * камера:
 *   ./state-driver "v4l2src device=/dev/video0 ! videoconvert ! autovideosink"
 */
#include <gst/gst.h>

typedef struct {
  GstElement *pipeline;  /* конвеєр, яким керуємо */
  GstBus     *bus;       /* його шина: окреме посилання, яке ми зобов'язані віддати */
  gboolean    is_live;   /* джерело живе → попереднього наповнення не буде ніколи */
  gboolean    quit;      /* цикл має завершитися */
  gboolean    failed;    /* завершуємося через помилку, а не через кінець потоку */
} Driver;
