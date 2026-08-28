// ── 2б. Зв'язок: дві підписки, прапорець і відписка ──
function bind<T extends object, K extends Extract<keyof T, string>>(
  el: HTMLInputElement,
  vm: T & { signals: Signals },
  prop: K,
  conv: Convert<T[K]>,
): () => void {
  if (!(prop in vm)) {                                   // одрук ловиться ТУТ, а не мовчки
    throw new Error(`bind: у моделі подання немає властивості «${prop}»`);
  }
  let writing = false;

  // властивість → поле
  const push = (v: unknown) => {
    const text = conv.toView(v as T[K]);
    if (el.value !== text) el.value = text;              // зайвий запис збиває каретку
  };
  const off = vm.signals.on(prop, push);

  // поле → властивість
  const onInput = () => {
    if (writing) return;                                 // друге коло не робимо
    writing = true;
    try { vm[prop] = conv.toModel(el.value); }           // ← ось сюди ставиться точка зупину
    finally { writing = false; }
  };
  el.addEventListener('input', onInput);

  push(vm[prop]);                                        // початкове наповнення поля
  return () => { off(); el.removeEventListener('input', onInput); };
}
