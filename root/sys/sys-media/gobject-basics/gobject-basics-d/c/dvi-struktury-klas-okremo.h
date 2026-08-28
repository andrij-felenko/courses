struct _GstElement {
  GstObject     object;        /* батьківська структура — першим полем */

  GRecMutex     state_lock;
  GstState      current_state;
  GstState      pending_state;
  GList        *pads;
  ...
};

struct _GstElementClass {
  GstObjectClass parent_class; /* батьківський клас — першим полем */

  GstMetadata   *metadata;
  GList         *padtemplates;

  /* віртуальні методи */
  GstPad             * (*request_new_pad) (GstElement *e, GstPadTemplate *t,
                                           const gchar *name, const GstCaps *caps);
  GstStateChangeReturn (*change_state)    (GstElement *e, GstStateChange transition);
  gboolean             (*send_event)      (GstElement *e, GstEvent *event);
  ...
};
