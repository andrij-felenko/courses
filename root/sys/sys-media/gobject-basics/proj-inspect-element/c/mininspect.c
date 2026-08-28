/* mininspect.c — власний gst-inspect на дві сотні рядків
   збірка: gcc mininspect.c -o mininspect $(pkg-config --cflags --libs gstreamer-1.0)
   запуск: ./mininspect filesrc                                                     */

#include <gst/gst.h>

static void print_ancestry (GType type);
static void print_pad_templates (GstElementClass * eclass);
static void print_properties (GObjectClass * oclass);
static void print_value_range (GParamSpec * p);
static void print_flags (GParamSpec * p);
static void print_signals (GType type);

int
main (int argc, char **argv)
{
  GstElementFactory *factory, *loaded;
  GObjectClass *oclass;
  GType type;

  /* Без цього немає нічого: ані таблиці типів GStreamer, ані реєстру.
     gst_init заразом з'їдає свої аргументи (--gst-debug-level тощо)
     з argv — тому його викликають ДО розбору власних аргументів.     */
  gst_init (&argc, &argv);

  if (argc != 2) {
    g_printerr ("вжиток: %s <ім'я елемента>\n", argv[0]);
    return 2;
  }

  factory = gst_element_factory_find (argv[1]);       /* посилання наше */
  if (!factory) {
    g_printerr ("елемента «%s» немає в реєстрі\n", argv[1]);
    return 1;
  }

  /* Реєстр знав лише метадані. Тепер вантажимо сам файл плагіна.
     Обережно: повертається ІНШИЙ об'єкт фабрики — той, що з
     завантаженого плагіна; старий треба відпустити.                  */
  loaded = GST_ELEMENT_FACTORY (
      gst_plugin_feature_load (GST_PLUGIN_FEATURE (factory)));
  gst_object_unref (factory);
  if (!loaded) {
    g_printerr ("плагін для «%s» не вантажиться\n", argv[1]);
    return 1;
  }
  factory = loaded;

  type = gst_element_factory_get_element_type (factory);  /* 0, якщо не завантажено */

  /* Ось де народжується структура класу: g_type_class_ref виконує
     class_init, а з ним — усі install_property і g_signal_new.       */
  oclass = g_type_class_ref (type);

  g_print ("%s — %s\n", argv[1],
      gst_element_factory_get_metadata (factory, GST_ELEMENT_METADATA_LONGNAME));
  g_print ("категорія: %s\n",
      gst_element_factory_get_metadata (factory, GST_ELEMENT_METADATA_KLASS));
  g_print ("плагін: %s\n",
      gst_plugin_feature_get_plugin_name (GST_PLUGIN_FEATURE (factory)));

  print_ancestry (type);
  print_pad_templates (GST_ELEMENT_CLASS (oclass));
  print_properties (oclass);
  print_signals (type);

  g_type_class_unref (oclass);   /* клас — не об'єкт, у нього свій лічильник */
  gst_object_unref (factory);
  return 0;
}
