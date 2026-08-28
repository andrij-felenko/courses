// Пункт 2 Effective Java: незмінний об'єкт із багатьма
// (переважно необов'язковими) полями, зібраний будівельником
public class NutritionFacts {
    private final int servingSize;   // обов'язкове
    private final int calories;      // необов'язкове
    private final int sodium;        // необов'язкове

    public static class Builder {
        private final int servingSize;   // обов'язкове — у конструкторі будівельника
        private int calories = 0;        // необов'язкові — зі значеннями за замовчуванням
        private int sodium   = 0;

        public Builder(int servingSize) {       // обов'язкове задаєш одразу
            this.servingSize = servingSize;
        }
        public Builder calories(int val) {       // крок повертає САМ будівельник...
            calories = val;
            return this;                         // ...тому виклики чіпляються в ланцюжок
        }
        public Builder sodium(int val) {
            sodium = val;
            return this;
        }
        public NutritionFacts build() {          // остаточне зібрання — тут
            return new NutritionFacts(this);     // єдина точка, де народжується об'єкт
        }
    }

    private NutritionFacts(Builder b) {          // приватний — назовні лише через build()
        servingSize = b.servingSize;
        calories    = b.calories;
        sodium      = b.sodium;
    }
}

// місце виклику читається саме себе:
NutritionFacts cola = new NutritionFacts.Builder(240)
        .calories(100)
        .sodium(35)
        .build();
