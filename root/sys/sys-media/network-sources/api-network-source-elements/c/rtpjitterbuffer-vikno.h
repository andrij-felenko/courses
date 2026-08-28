GstStructure *stats = NULL;
guint64 pushed = 0, lost = 0, late = 0, dup = 0;

g_object_get (jitterbuffer, "stats", &stats, NULL);
gst_structure_get (stats,
    "num-pushed", G_TYPE_UINT64, &pushed,
    "num-lost", G_TYPE_UINT64, &lost,
    "num-late", G_TYPE_UINT64, &late,
    "num-duplicates", G_TYPE_UINT64, &dup, NULL);
gst_structure_free (stats);      /* структуру віддають у власність — звільняти обов'язково */
