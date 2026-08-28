    def _guard(self):
        """Спрацьовує один раз, якщо за guard_sec секунд PLAYING так і не настав."""
        # НУЛЬОВА витримка: питаємо, що є ЗАРАЗ, і не чекаємо ні миті.
        # Gst.CLOCK_TIME_NONE тут означало б «висни разом із конвеєром».
        ret, cur, pending = self.pipeline.get_state(0)

        print(f"СТОРОЖ: за {self.guard_sec} с конвеєр не дійшов до PLAYING",
              file=sys.stderr)
        print(f"  зараз:   {Gst.Element.state_get_name(cur)}", file=sys.stderr)
        print(f"  у черзі: {Gst.Element.state_get_name(pending)}", file=sys.stderr)
        print(f"  перехід: {Gst.Element.state_change_return_get_name(ret)}",
              file=sys.stderr)

        if cur == Gst.State.PAUSED and not self.is_live:
            print("  → перший буфер не дійшов до стоку: розрив десь між ними",
                  file=sys.stderr)
        elif cur == Gst.State.PAUSED:
            print("  → джерело живе, PAUSED тут не діагноз: дивись, чому нема PLAYING",
                  file=sys.stderr)
        elif cur == Gst.State.READY:
            print("  → не вийшли з READY: джерело не відкрилося", file=sys.stderr)
        elif cur == Gst.State.NULL:
            print("  → конвеєр у NULL: set_state або не викликали, або він відкотився",
                  file=sys.stderr)

        self._dump("stuck")
        self.guard_id = 0
        return GLib.SOURCE_REMOVE          # доповіли один раз — далі не набридаємо
