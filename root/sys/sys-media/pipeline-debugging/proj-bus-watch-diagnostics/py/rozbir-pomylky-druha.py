    def _report(self, msg, kind):
        """Розбір ERROR / WARNING / INFO."""
        if msg.type == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
        elif msg.type == Gst.MessageType.WARNING:
            err, dbg = msg.parse_warning()
        else:
            err, dbg = msg.parse_info()

        print(f"{kind}: {err.message}", file=sys.stderr)
        print(f"  елемент: {self._src_path(msg)}", file=sys.stderr)
        print(f"  домен:   {err.domain}, код {err.code}", file=sys.stderr)
        # Ось заради чого все: файл, рядок, функція і шлях у графі.
        print(f"  місце:   {dbg or '(бібліотека не дала подробиць)'}", file=sys.stderr)
