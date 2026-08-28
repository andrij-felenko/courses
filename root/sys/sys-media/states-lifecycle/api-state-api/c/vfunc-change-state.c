ret = GST_ELEMENT_CLASS (parent_class)->change_state (element, transition);
if (ret == GST_STATE_CHANGE_FAILURE)
  return ret;

if (self->is_live &&
    (transition == GST_STATE_CHANGE_READY_TO_PAUSED ||
     transition == GST_STATE_CHANGE_PLAYING_TO_PAUSED))
  ret = GST_STATE_CHANGE_NO_PREROLL;

return ret;
