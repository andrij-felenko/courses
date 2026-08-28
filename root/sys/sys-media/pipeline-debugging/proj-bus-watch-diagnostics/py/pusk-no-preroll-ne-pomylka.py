    def start(self):
        """Пуск із розбором відповіді. False — конвеєр навіть не почав."""
        ret = self.pipeline.set_state(Gst.State.PAUSED)

        if ret == Gst.StateChangeReturn.NO_PREROLL:
            self.is_live = True
            print("джерело живе: прероллу не буде, ASYNC_DONE теж не прийде",
                  file=sys.stderr)

        if ret != Gst.StateChangeReturn.FAILURE:
            ret = self.pipeline.set_state(Gst.State.PLAYING)

        if ret == Gst.StateChangeReturn.FAILURE:
            # Помилка вже на шині, але головний цикл ще не крутиться, і стеження,
            # хоч і приєднане, не спрацює. Забираємо руками — тією ж функцією.
            msg = self.bus.timed_pop_filtered(0, Gst.MessageType.ERROR)
            if msg is not None:
                self._report(msg, "ПОМИЛКА ПУСКУ")
            else:
                print("пуск не вдався, а помилки на шині немає", file=sys.stderr)
            self._dump("start-failed")
            return False
        return True
