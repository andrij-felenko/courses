class IdAllocator:
    """Один CAS у ядро на цілий блок; далі — локальна лічба без раундів."""
    def __init__(self, core, key="/dh/id-block", block=1000):
        self.core, self.key, self.block = core, key, block
        self.next = self.end = 0                 # порожньо → перший mint візьме блок

    async def mint(self) -> int:
        if self.next >= self.end:                # блок вичерпано (раз на 1000 разів)
            await self._lease_block()            # ← єдиний дотик до щабля 2
        v, self.next = self.next, self.next + 1  # ← 999 разів із 1000: чиста локальна лічба
        return v

    async def _lease_block(self):
        while True:                              # CAS-цикл: атомарно посунути «водомір»
            hi, rev = await self.core.get(self.key)
            hi = int(hi or 0)
            new_rev, ok = await self.core.cas(self.key, str(hi + self.block), expect_rev=rev)
            if ok:
                self.next, self.end = hi, hi + self.block
                return
