// util.ts — власний дедлайн поверх будь-якого проміса, без «підвислих» таймерів
export function withTimeout<T>(p: Promise<T>, ms: number): Promise<T> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new HubTimeout(`хаб мовчить ${ms} мс`)), ms);
    p.then(
      (v) => { clearTimeout(t); resolve(v); },
      (e) => { clearTimeout(t); reject(e); },
    );
  });
}
