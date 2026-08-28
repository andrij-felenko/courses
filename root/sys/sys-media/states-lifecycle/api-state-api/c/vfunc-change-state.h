struct _GstElementClass {
  /* ... */
  GstStateChangeReturn (*change_state) (GstElement    *element,
                                        GstStateChange transition);
  GstStateChangeReturn (*set_state)    (GstElement    *element,
                                        GstState       state);
  GstStateChangeReturn (*get_state)    (GstElement    *element,
                                        GstState      *state,
                                        GstState      *pending,
                                        GstClockTime   timeout);
  void                 (*state_changed)(GstElement    *element,
                                        GstState       oldstate,
                                        GstState       newstate,
                                        GstState       pending);
};
