class Autoplug:                                   # продовження класу
    def dump_topology(self, element=None, depth=0):
        if element is None:
            print("\n── топологія після no-more-pads ─────────────")
            element = self.pipeline
        # Ітерацію по Gst.Iterator додають перевизначення з gst-python;
        # без цього пакунка тут був би TypeError: 'Iterator' object is not iterable.
        for child in element.iterate_sorted():
            f = child.get_factory()
            print("%s%s  (%s)" % ("  " * (depth + 1), child.get_name(),
                                  f.get_name() if f else "—"))
            if isinstance(child, Gst.Bin):
                self.dump_topology(child, depth + 1)
        return GLib.SOURCE_REMOVE

    def on_no_more_pads(self, dec):
        # Ми в потоці даних — довгу роботу віддаємо головному циклу.
        GLib.idle_add(self.dump_topology)

    def on_unknown_type(self, dec, pad, caps):
        self.note("нема чим декодувати: %s" % caps.to_string())
        self.exit_code = 2

    def on_message(self, bus, msg):
        if msg.type == Gst.MessageType.ELEMENT:
            if GstPbutils.is_missing_plugin_message(msg):
                self.missing = GstPbutils.missing_plugin_message_get_description(msg)
                detail = GstPbutils.missing_plugin_message_get_installer_detail(msg)
                print("бракує: %s" % self.missing)
                if detail:
                    print("  рядок для встановлювача: %s" % detail)
        elif msg.type == Gst.MessageType.ERROR:
            err, _dbg = msg.parse_error()
            print("помилка від %s: %s" % (msg.src.get_name(), err.message),
                  file=sys.stderr)
            if self.missing:
                print("  найімовірніша причина: у системі немає %s" % self.missing,
                      file=sys.stderr)
            self.exit_code = 1
            self.loop.quit()
        elif msg.type == Gst.MessageType.EOS:
            self.loop.quit()
