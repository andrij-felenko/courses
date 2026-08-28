class RingBuffer:
    """Дескриптор C-буфера плюс усе, що C-код тримає за адресою."""

    def __init__(self, cap, storage=None):
        self._storage = storage          # ← живе рівно стільки, скільки живе _h
        if storage is None:
            self._h = lib.rb_create(cap)
        else:
            self._h = lib.rb_create_static(storage, cap)
        if not self._h:                  # NULL-покажчик у ctypes хибний
            raise MemoryError("бібліотека повернула NULL замість буфера")
        self._out = u8()                 # один буфер під результат pop на весь час життя

    def push(self, value):
        """True, якщо найстаріший байт витіснено."""
        return lib.rb_push(self._h, value) == 1

    def pop(self):
        """Байт або None, якщо буфер порожній."""
        if lib.rb_pop(self._h, ctypes.byref(self._out)) != 0:
            return None
        return self._out.value

    def __len__(self):
        return lib.rb_len(self._h)

    def close(self):
        if self._h:
            lib.rb_destroy(self._h)
            self._h = None
        self._storage = None
