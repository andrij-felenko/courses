/* transfer full — список фабрик, УЖЕ впорядкований за спаданням рангу */
GList *gst_element_factory_list_get_elements (GstElementFactoryListType type,
                                              GstRank minrank);

/* transfer full — новий список; вхідний НЕ споживається і НЕ звільняється */
GList *gst_element_factory_list_filter       (GList *list,
                                              const GstCaps *caps,
                                              GstPadDirection direction,
                                              gboolean subsetonly);

/* та сама перевірка виду для однієї фабрики */
gboolean gst_element_factory_list_is_type    (GstElementFactory *factory,
                                              GstElementFactoryListType type);
