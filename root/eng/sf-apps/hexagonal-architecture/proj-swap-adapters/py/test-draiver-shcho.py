# Підробка, що імітує збій сховища — теж просто реалізація порту
class ПадучеСховище(ЗамовленняСховище):
    async def зберегти(self, з): raise RuntimeError("база впала")
    async def узяти(self, id): return None


@pytest.mark.asyncio
async def test_збій_сховища_проноситься_нагору():
    сервіс = ЗамовленняСервіс(ПадучеСховище(), lambda: "1")
    with pytest.raises(RuntimeError, match="база впала"):
        await сервіс.оформити("a@b.com", [Позиція("x", 1, 1)])
