import hashlib, struct, sys

class Cursor:
    def __init__(self, blob, order):
        self.b, self.o, self.order = blob, 0, order

    def u32(self):
        v = struct.unpack_from(self.order + "I", self.b, self.o)[0]
        self.o += 4
        return v

    def take(self, n):
        v = self.b[self.o:self.o + n]
        self.o += n
        return v

    def more(self):
        return self.o < len(self.b)


def entries(blob, dlen):
    if not blob:
        return
    # журнал написано в порядку байтів тієї машини; номер регістра малий,
    # тож чужий порядок видно вже з першого поля
    order = "<" if struct.unpack_from("<I", blob, 0)[0] < 256 else ">"
    c, n = Cursor(blob, order), 0
    while c.more():
        n += 1
        pcr = c.u32()
        digest = c.take(dlen)
        name = c.take(c.u32()).decode("ascii")
        if name == "ima":                              # найдавніший шаблон
            body = c.take(20) + c.take(c.u32()).ljust(256, b"\x00")
        else:
            body = c.take(c.u32())                     # пари «довжина + поле» підряд
        yield n, pcr, digest, name, body
