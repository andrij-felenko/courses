class Autoplug:                                   # продовження класу
    def make_tail(self, names):
        branch, prev = Gst.Bin.new(None), None
        for n in names:
            e = Gst.ElementFactory.make(n, None)
            if e is None:
                raise RuntimeError("немає елемента " + n)
            branch.add(e)
            if prev is None:
                branch.add_pad(Gst.GhostPad.new("sink", e.get_static_pad("sink")))
            elif not prev.link(e):
                raise RuntimeError("не з'єдналися: %s → %s" % (prev.get_name(), n))
            prev = e
        return branch

    def on_pad_added(self, dec, pad):
        caps = pad.get_current_caps() or pad.query_caps(None)
        media = caps.get_structure(0).get_name()

        if media.startswith("video/x-raw"):
            names = VIDEO_TAIL
        elif media.startswith("audio/x-raw"):
            names = AUDIO_TAIL
        else:
            self.note("пад %s: %s — хвоста для такого немає"
                      % (pad.get_name(), media))
            return

        branch = self.make_tail(names)
        self.pipeline.add(branch)               # 1. у конвеєр
        branch.sync_state_with_parent()         # 2. догнати стан конвеєра
        if pad.link(branch.get_static_pad("sink")) == Gst.PadLinkReturn.OK:
            self.note("пад %s: %s → %s" % (pad.get_name(), media, " ! ".join(names)),
                      branches=1)               # 3. і лише тепер лінк
        else:
            print("пад %s не приєднався" % pad.get_name(), file=sys.stderr)
