def on_bus_message(bus, msg, loop):
    if msg.type == Gst.MessageType.ERROR:
        err, dbg = msg.parse_error()
        print(f"помилка від {msg.src.name}: {err.message}")
        print(f"подробиці: {dbg or '(немає)'}")
        loop.quit()
    elif msg.type == Gst.MessageType.EOS:
        print("потік скінчився")
        loop.quit()
    return True                    # лишаємося підключеними

bus = pipeline.get_bus()
bus.add_watch(GLib.PRIORITY_DEFAULT, on_bus_message, loop)
