import copy

class Monster:
    def __deepcopy__(self, memo):
        new = Monster.__new__(Monster)
        memo[id(self)] = new             # ЗАРЕЄСТРУВАТИ до рекурсії — інакше цикл зламає
        new.name = self.name             # скаляри — як є
        new.hp = self.hp
        new.stats = copy.deepcopy(self.stats, memo)  # углиб, з тим самим memo
        new.loot = list(self.loot)
        new.squad = copy.deepcopy(self.squad, memo)  # цикл: memo поверне вже створений new
        return new
