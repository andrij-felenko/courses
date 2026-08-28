def check_layout():
    """Звірити уявлення обв'язки про структуру з тим, що каже сам C-код."""
    want, got = lib.rb_sizeof(), ctypes.sizeof(RB)
    if got != want:
        raise AssertionError(f"sizeof(struct rb): C каже {want}, ctypes рахує {got}")
    for name, _ in RB._fields_:
        want = lib.rb_offset(name.encode("ascii"))
        got  = getattr(RB, name).offset
        if got != want:
            raise AssertionError(f"зсув поля {name}: C каже {want}, ctypes рахує {got}")


check_layout()
