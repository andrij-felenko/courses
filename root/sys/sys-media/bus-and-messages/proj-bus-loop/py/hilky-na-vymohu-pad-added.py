    def add_branch(self, factories):
        """Будує ланцюжок, лінкує його й підтягує стан під конвеєр.
        Повертає вхідний pad першого елемента."""
        chain = []
        for name in factories:
            element = Gst.ElementFactory.make(name)
            if element is None:
                print(f"бракує елемента «{name}» — не встановлено плагін", file=sys.stderr)
                return None
            self.pipeline.add(element)
            if chain and not chain[-1].link(element):
                print(f"не з'єдналися {chain[-1].name} і {name}", file=sys.stderr)
                return None
            chain.append(element)

        # стан підтягуємо ТІЛЬКИ після з'єднання всього ланцюжка
        for element in chain:
            element.sync_state_with_parent()
        return chain[0].get_static_pad("sink")

    def on_pad_added(self, dec, pad):
        """Викликається в НИТЦІ ПОТОКУ uridecodebin, не в головній."""
        caps = pad.get_current_caps() or pad.query_caps(None)
        media = caps.get_structure(0).get_name()

        if media.startswith("video/"):
            want, label = ["queue", "videoconvert", "autovideosink"], "відео"
        elif media.startswith("audio/"):
            want, label = ["queue", "audioconvert", "audioresample", "autoaudiosink"], "звук"
        else:
            return                       # субтитри й службові потоки не беремо

        sink = self.add_branch(want)
        if sink is None:
            return
        if pad.link(sink) != Gst.PadLinkReturn.OK:
            print(f"гілку «{label}» не приєднано", file=sys.stderr)
