class Borg:
    _shared = {}                       # один словник на весь клас
    def __init__(self):
        self.__dict__ = Borg._shared   # усі екземпляри ділять один і той самий __dict__

class Settings(Borg):
    def __init__(self):
        super().__init__()
        if not hasattr(self, "theme"):
            self.theme = "light"       # ініціалізуємо лише вперше

a = Settings(); b = Settings()
a.theme = "dark"
print(b.theme)        # "dark" — хоча b створювали окремо: стан у них спільний
print(a is b)         # False — це РІЗНІ об'єкти з однаковим станом
