if __name__ == "__main__":
    import os

    if len(sys.argv) < 2:
        print(f'вжиток: {sys.argv[0]} "<опис конвеєра для gst-launch>"', file=sys.stderr)
        sys.exit(2)

    os.makedirs("/tmp/gstdiag", exist_ok=True)              # GStreamer теку НЕ створює
    os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp/gstdiag"   # ПЕРЕД Gst.init
    Gst.init(None)

    loop = GLib.MainLoop()
    pipeline = Gst.parse_launch(sys.argv[1])

    diag = Diag(pipeline, "cam0", guard_sec=10)             # сторож на 10 секунд
    if diag.start():
        loop.run()                                          # без цього рядка обв'язка мертва

    pipeline.set_state(Gst.State.NULL)
    diag.detach()
