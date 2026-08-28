class Autoplug:                                   # продовження класу
    def veto_reason(self, factory):
        if self.no_hw and Gst.ElementFactory.list_is_type(
                factory, Gst.ELEMENT_FACTORY_TYPE_HARDWARE):
            return "апаратний (--no-hw)"
        name = factory.get_name()
        if any(name.startswith(p) for p in self.veto):
            return "у списку --skip"
        return None

    def on_select(self, dec, pad, caps, factory):
        # caps і factory належать decodebin: посилання на них тримати
        # після повернення з колбека не можна — беріть значення, не об'єкти.
        name = factory.get_name()
        rank = factory.get_rank()
        klass = factory.get_metadata(Gst.ELEMENT_METADATA_KLASS)
        media = caps.get_structure(0).get_name()
        why = self.veto_reason(factory)

        self.note("%-22s %-14s ранг %-5d %-30s %s" % (
                      media, name, rank, klass,
                      "ПРОПУСК — " + why if why else "спроба"),
                  tried=0 if why else 1, skipped=1 if why else 0)
        return SKIP if why else TRY
