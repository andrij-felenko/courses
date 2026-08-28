class Stats:
    def __init__(self, attack, defense, resist):
        self.attack = attack
        self.defense = defense
        self.resist = resist            # вкладений ЗМІННИЙ dict опорів

    def clone(self):
        # глибоко: власний новий dict, а не спільний з оригіналом
        return Stats(self.attack, self.defense, dict(self.resist))

class Monster:
    def __init__(self, name, hp, stats, loot):
        self.name = name                # рядок незмінний — просто значення
        self.hp = hp                    # число — просто значення
        self.stats = stats              # вкладений об'єкт
        self.loot = loot                # вкладений список

    def clone(self):
        return Monster(
            self.name, self.hp,
            self.stats.clone(),         # глибоко: власний Stats
            list(self.loot),            # глибоко: власний список
        )
