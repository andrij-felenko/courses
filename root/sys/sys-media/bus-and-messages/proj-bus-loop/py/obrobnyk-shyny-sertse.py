    def report_error(self, msg):
        """Розбір помилки. Повідомлення не звільняє — власник у різних дорогах різний."""
        err, dbg = msg.parse_error()

        print(f"ПОМИЛКА від {msg.src.name}: {err.message}", file=sys.stderr)
        print(f"  домен {err.domain}, код {err.code}", file=sys.stderr)

        if err.domain == "gst-resource-error-quark" and err.code == Gst.ResourceError.NOT_FOUND:
            print("  → за цією адресою джерела немає", file=sys.stderr)
        elif err.domain == "gst-stream-error-quark" and err.code == Gst.StreamError.CODEC_NOT_FOUND:
            print("  → у системі немає плагіна-декодера для цього формату", file=sys.stderr)

        print(f"  зневадження: {dbg or '(немає)'}", file=sys.stderr)

    def on_message(self, bus, msg, _unused):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            self.report_error(msg)
            self.exit_code = 1
            self.loop.quit()                      # конвеєр сам не спиниться

        elif t == Gst.MessageType.EOS:
            print("кінець потоку")
            self.loop.quit()

        elif t == Gst.MessageType.WARNING:
            err, dbg = msg.parse_warning()
            print(f"попередження від {msg.src.name}: {err.message} ({dbg or '—'})",
                  file=sys.stderr)                # робота триває — не зупиняємо

        elif t == Gst.MessageType.STATE_CHANGED:
            if msg.src is not self.pipeline:
                return True                       # стани окремих елементів нас не цікавлять
            old, new, _pending = msg.parse_state_changed()
            print(f"конвеєр: {Gst.Element.state_get_name(old)} → "
                  f"{Gst.Element.state_get_name(new)}")

        elif t == Gst.MessageType.BUFFERING:
            if self.is_live:
                return True                       # живому джерелу пауза лише зашкодить
            percent = msg.parse_buffering()
            print(f"буферизація {percent:3d}%")

            if percent < 100:
                if not self.buffering and self.target == Gst.State.PLAYING:
                    self.pipeline.set_state(Gst.State.PAUSED)
                self.buffering = True
            elif self.buffering:
                self.buffering = False
                if self.target == Gst.State.PLAYING:
                    self.pipeline.set_state(Gst.State.PLAYING)

        elif t == Gst.MessageType.LATENCY:
            print(f"перерахунок затримки на прохання {msg.src.name}")
            self.pipeline.recalculate_latency()

        elif t == Gst.MessageType.CLOCK_LOST:
            # годинник зник; новий вибереться на наступному вході в PLAYING
            self.pipeline.set_state(Gst.State.PAUSED)
            self.pipeline.set_state(Gst.State.PLAYING)

        return True                               # лишаємось підключеними
