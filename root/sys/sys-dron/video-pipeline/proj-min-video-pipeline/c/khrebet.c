#include <gst/gst.h>

typedef struct {
    GstElement *pipeline, *tee;
    GstElement *view_q, *view_valve, *decode, *convert, *view_sink;
    GstElement *rec_q, *rec_valve, *rec_sink;   /* rec_sink живе лише під час запису */
    gboolean    rec_closing;                    /* чекаємо підтвердження про закриття файлу */
    guint       rec_deadline;
    GMainLoop  *loop;
} App;

static gboolean build_backbone(App *a)
{
    a->pipeline = gst_pipeline_new("video");

    GstElement *src   = gst_element_factory_make("udpsrc",          "src");
    GstElement *jbuf  = gst_element_factory_make("rtpjitterbuffer", "jbuf");
    GstElement *depay = gst_element_factory_make("rtph264depay",    "depay");
    GstElement *parse = gst_element_factory_make("h264parse",       "parse");
    a->tee            = gst_element_factory_make("tee",             "tee");

    if (!a->pipeline || !src || !jbuf || !depay || !parse || !a->tee)
        return FALSE;

    /* Потік про себе нічого не каже: у чистому UDP немає опису сесії,
       тож відповідність «тип навантаження → кодек» задаємо руками. */
    GstCaps *caps = gst_caps_from_string(
        "application/x-rtp, media=(string)video, clock-rate=(int)90000, "
        "encoding-name=(string)H264, payload=(int)96");
    g_object_set(src, "port", 5600, "caps", caps, NULL);
    gst_caps_unref(caps);                 /* g_object_set узяв власне посилання */

    g_object_set(jbuf, "latency",         80,     /* мс запасу — єдина навмисна затримка */
                       "do-lost",         TRUE,   /* сказати декодерові про дірку */
                       "drop-on-latency", TRUE,   /* спізнілий пакет не тримає потік */
                       NULL);

    /* Ми приєднуємось до потоку, який уже йде: набори параметрів мають
       повторюватись на кожному ключовому кадрі, інакше чекати вічно. */
    g_object_set(parse, "config-interval", -1, NULL);

    /* Поки жодну гілку не під'єднано, трійникові немає куди штовхати. */
    g_object_set(a->tee, "allow-not-linked", TRUE, NULL);

    gst_bin_add_many(GST_BIN(a->pipeline), src, jbuf, depay, parse, a->tee, NULL);
    return gst_element_link_many(src, jbuf, depay, parse, a->tee, NULL);
}
