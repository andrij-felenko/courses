interface Node {
  id: string;                      // Унікальний ідентифікатор вузла в межах екрана
  type: string;                    // Назва компонента для пошуку в Component Registry
  props?: Record<string, any>;     // Статичні властивості та конфігурація віджета
  bind?: {                         // Декларативне зв'язування з клієнтським станом
    value?: string;                // JSON Pointer до поля в сховищі стану (наприклад, "/user/email")
    [propName: string]: string | undefined;
  };
  visibility?: Expression;         // Логічний AST-вираз; результат false виключає вузол з рендер-дерева
  enabled?: Expression;            // Логічний AST-вираз; результат false блокує взаємодію (disabled-стан)
  validation?: ValidationRule[];   // Список декларативних правил перевірки коректності значення
  actions?: Record<string, Action>;// Обробники подій ("on_click", "on_change", "on_blur", "on_mount")
  children?: Node[];               // Вкладені дочірні вузли для контейнерних елементів
  fallback?: Node;                 // Запасний вузол для застарілих клієнтів, якщо type не зареєстровано
}
