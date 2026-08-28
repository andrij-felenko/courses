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
