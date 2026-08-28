/**
 * Синхронізація властивостей між старим і новим набором
 */
export function patchProps(
  el: HTMLElement,
  oldProps: VNodeProps,
  newProps: VNodeProps
): void {
  // Фаза 1: Видалення властивостей, яких більше немає
  for (const key of Object.keys(oldProps)) {
    if (key === "key") continue;
    if (!(key in newProps)) {
      if (key.startsWith("on")) {
        const eventName = key.slice(2).toLowerCase();
        el.removeEventListener(eventName, oldProps[key]);
      } else if (key === "className") {
        el.removeAttribute("class");
      } else if (key === "style") {
        el.removeAttribute("style");
      } else {
        el.removeAttribute(key);
      }
    }
  }

  // Фаза 2: Додавання та оновлення нових властивостей
  for (const [key, value] of Object.entries(newProps)) {
    if (key === "key") continue;
    const oldValue = oldProps[key];
    if (oldValue === value) continue;

    if (key.startsWith("on")) {
      const eventName = key.slice(2).toLowerCase();
      if (oldValue) el.removeEventListener(eventName, oldValue);
      if (value) el.addEventListener(eventName, value);
    } else if (key === "className") {
      el.className = value || "";
    } else if (key === "style" && typeof value === "object") {
      // Очищення видалених CSS-властивостей всередині об'єкта style
      if (typeof oldValue === "object" && oldValue !== null) {
        for (const styleKey of Object.keys(oldValue)) {
          if (!(styleKey in value)) {
            (el.style as any)[styleKey] = "";
          }
        }
      }
      Object.assign(el.style, value);
    } else if (typeof value === "boolean") {
      // Обробка булевих атрибутів (disabled, checked тощо)
      if (value) {
        el.setAttribute(key, "");
        (el as any)[key] = true;
      } else {
        el.removeAttribute(key);
        (el as any)[key] = false;
      }
    } else {
      el.setAttribute(key, String(value));
    }
  }
}
