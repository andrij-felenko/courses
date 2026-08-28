// Клієнт написаний під ArrayList і вірить його контракту:
// «дали список — у нього можна додавати».
function fill(list: ArrayList<number>, n: number): void {
  for (let i = 0; i < n; i++) {
    list.add(i);                    // контракт ArrayList це дозволяє
  }
}

const normal = new ArrayList<number>();
fill(normal, 3);                    // ок: [0, 1, 2]
console.log(normal.size());         // 3

const frozen = new ImmutableList<number>([10, 20]);
fill(frozen, 3);                    // ← ВИБУХ: Error на першому ж add
