sink = pipeline.get_by_name("out")
sink.set_property("sync", False)
sink.set_property("max-buffers", 2)

while True:
    sample = sink.emit("try-pull-sample", Gst.SECOND)
    if sample is None:                 # таймаут або кінець потоку
        if sink.get_property("eos"):
            break
        continue

    buf = sample.get_buffer()
    ok, info = buf.map(Gst.MapFlags.READ)
    if ok:
        process(info.data)             # memoryview на пам'ять буфера
        buf.unmap(info)
    del sample                         # не тримати посилання довше, ніж треба
