// «Бренд» — фантомне поле лише для перевірки типів; у рантаймі його немає.
type Brand<T, B> = T & { readonly __unit: B };

type NewtonSeconds     = Brand<number, "N·s">;
type PoundForceSeconds = Brand<number, "lbf·s">;

// Конструктори — єдиний спосіб «охрестити» голе число одиницею.
const ns   = (x: number) => x as NewtonSeconds;
const lbfs = (x: number) => x as PoundForceSeconds;

// Єдиний дозволений місток — явний перевід із коефіцієнтом.
const toNs = (x: PoundForceSeconds): NewtonSeconds => ns(x * 4.448222);

// Навігація приймає ЛИШЕ ньютон-секунди — це записано в типі аргументу.
function applyImpulse(j: NewtonSeconds) {
    /* ... коригуємо траєкторію, знаючи, що j — точно в Н·с ... */
}

// applyImpulse(lbfs(1.85));          // ← ПОМИЛКА ТИПУ:
//   'PoundForceSeconds' is not assignable to 'NewtonSeconds'
applyImpulse(toNs(lbfs(1.85)));       // ✓ перевід явний
applyImpulse(ns(8.23));               // ✓ вже в Н·с
