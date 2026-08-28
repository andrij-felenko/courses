    def _on_message(self, bus, msg, _unused):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            self._report(msg, "ПОМИЛКА")
            self._dump("error")                    # докази — у мілісекунду аварії

        elif t == Gst.MessageType.WARNING:
            self._report(msg, "ПОПЕРЕДЖЕННЯ")

        elif t == Gst.MessageType.INFO:
            self._report(msg, "ВІДОМІСТЬ")

        elif t == Gst.MessageType.ELEMENT:
            if GstPbutils.is_missing_plugin_message(msg):
                desc = GstPbutils.missing_plugin_message_get_description(msg)
                inst = GstPbutils.missing_plugin_message_get_installer_detail(msg)
                print(f"БРАКУЄ ПЛАГІНА: {desc}", file=sys.stderr)
                print(f"  рядок для встановлювача: {inst}", file=sys.stderr)
                self._dump("missing-plugin")

        elif t == Gst.MessageType.QOS:
            now = GLib.get_monotonic_time()
            if now - self.qos_last < 1_000_000:     # не частіше ніж раз на секунду
                return True
            self.qos_last = now

            fmt, processed, dropped = msg.parse_qos_stats()
            if fmt == Gst.Format.UNDEFINED:
                return True                          # елемент лічби не веде
            jitter, proportion, _quality = msg.parse_qos_values()
            print(f"QoS {self._src_path(msg)} [{fmt.value_nick}]: "
                  f"оброблено {processed}, викинуто {dropped}; "
                  f"запізнення {jitter / 1e6:.1f} мс, темп ×{proportion:.2f}",
                  file=sys.stderr)

        elif t == Gst.MessageType.STATE_CHANGED:
            if msg.src is not self.pipeline:
                return True                          # стани окремих елементів — не наша справа
            old, new, _pending = msg.parse_state_changed()
            print(f"конвеєр: {Gst.Element.state_get_name(old)} → "
                  f"{Gst.Element.state_get_name(new)}", file=sys.stderr)
            if new == Gst.State.PLAYING and self.guard_id:
                GLib.source_remove(self.guard_id)     # доїхали — сторож не потрібен
                self.guard_id = 0

        return True                                  # лишаємось підключеними
