  /* Крок 2: у PLAYING. ASYNC тут — не біда: доводити перехід до кінця
     буде цикл нижче, а нам чекати нема потреби. */
  ret = gst_element_set_state (d.pipeline, GST_STATE_PLAYING);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("перехід у PLAYING провалився\n");
    drain_bus (&d);
    rc = 1;
    goto teardown;
  }

  /* Крок 3: живемо, поки шина не скаже інакше. */
  while (!d.quit) {
    GstMessage *msg = gst_bus_timed_pop_filtered (d.bus, 100 * GST_MSECOND,
                                                  GST_MESSAGE_ANY);
    if (msg == NULL) {
      /* сюди потрапляємо десять разів на секунду: місце для власної
         періодичної роботи — опитати позицію, оновити вікно, глянути прапорці */
      continue;
    }

    handle_message (&d, msg);
    gst_message_unref (msg);
  }

  if (d.failed)
    rc = 1;

teardown:
  /* Крок 4: униз до NULL — і лише потім віддавати посилання. */
  gst_element_set_state (d.pipeline, GST_STATE_NULL);
  gst_object_unref (d.bus);
  gst_object_unref (d.pipeline);

  return rc;
}
