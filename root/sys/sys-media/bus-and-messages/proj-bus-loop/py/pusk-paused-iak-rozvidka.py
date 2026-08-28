    def run(self):
        ret = self.pipeline.set_state(Gst.State.PAUSED)

        if ret == Gst.StateChangeReturn.FAILURE:
            # головного циклу ще нема, забрати повідомлення нікому — беремо самі
            msg = self.bus.timed_pop_filtered(0, Gst.MessageType.ERROR)
            if msg is not None:
                self.report_error(msg)   # звільняє зв'язувач, коли обгортка помре
            else:
                print("конвеєр не пішов у PAUSED, а помилки на шині немає", file=sys.stderr)
            self.exit_code = 1
        else:
            self.is_live = (ret == Gst.StateChangeReturn.NO_PREROLL)
            self.pipeline.set_state(Gst.State.PLAYING)
            self.loop.run()              # уся програма живе тут

        # однаковий шлях і після помилки, і після EOS
        self.pipeline.set_state(Gst.State.NULL)
        self.bus.remove_watch()
        return self.exit_code


def main():
    Gst.init(None)
    if len(sys.argv) < 2:
        print(f"вжиток: {sys.argv[0]} <uri>", file=sys.stderr)
        return 2
    return Player(sys.argv[1]).run()


if __name__ == "__main__":
    sys.exit(main())
