interface Repository { fun load(id: Int): String }

class CachingRepository(private val inner: Repository) : Repository by inner {
    // усі методи Repository автоматично переслано в inner;
    // перевизначаємо руками ЛИШЕ те, що справді міняємо:
    override fun load(id: Int): String {
        println("спершу глянули б у кеш")
        return inner.load(id)
    }
}
