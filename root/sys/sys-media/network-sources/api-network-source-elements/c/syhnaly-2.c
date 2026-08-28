static void
on_new_jitterbuffer (GstElement * rtpbin, GstElement * jb,
    guint session, guint ssrc, gpointer user_data)
{
  g_object_set (jb, "max-misorder-time", 500, "faststart-min-packets", 3, NULL);
}

static void
on_new_manager (GstElement * src, GstElement * manager, gpointer user_data)
{
  g_signal_connect (manager, "new-jitterbuffer",
      G_CALLBACK (on_new_jitterbuffer), NULL);
}
