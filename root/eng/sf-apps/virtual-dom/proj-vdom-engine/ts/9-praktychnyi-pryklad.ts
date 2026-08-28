interface TodoItem {
  id: number;
  title: string;
  completed: boolean;
}

class TodoApp {
  private state: { todos: TodoItem[]; count: number } = {
    todos: [
      { id: 1, title: "Написати VDOM рушій", completed: true },
      { id: 2, title: "Реалізувати алгоритм узгодження", completed: true },
      { id: 3, title: "Оптимізувати роботу зі списками через key", completed: false },
    ],
    count: 0,
  };

  private vnode: VNode | null = null;
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
  }

  setState(updater: (prev: typeof this.state) => void): void {
    updater(this.state);
    scheduler.schedule(() => this.render());
  }

  private render(): void {
    const newVNode = h(
      "div",
      { className: "todo-app" },
      h("h1", null, "Список завдань (Оновлень: ", this.state.count, ")"),
      h(
        "div",
        { className: "toolbar", style: { marginBottom: "15px" } },
        h(
          "button",
          {
            onClick: () => {
              this.setState((s) => {
                s.count++;
                s.todos.reverse(); // Реверс порядку для перевірки key-переміщень
              });
            },
          },
          "Розвернути список"
        ),
        h(
          "button",
          {
            onClick: () => {
              this.setState((s) => {
                s.count++;
                s.todos.unshift({
                  id: Date.now(),
                  title: `Нове завдання #${s.todos.length + 1}`,
                  completed: false,
                });
              });
            },
          },
          "Додати на початок"
        )
      ),
      h(
        "ul",
        { className: "todo-list" },
        this.state.todos.map((todo) =>
          h(
            "li",
            {
              key: todo.id,
              className: todo.completed ? "completed" : "",
              style: { padding: "6px 0" },
            },
            h("input", {
              type: "checkbox",
              checked: todo.completed,
              onClick: () => {
                this.setState((s) => {
                  s.count++;
                  const item = s.todos.find((t) => t.id === todo.id);
                  if (item) item.completed = !item.completed;
                });
              },
            }),
            h("span", { style: { marginLeft: "8px" } }, todo.title)
          )
        )
      )
    );

    patch(this.container, newVNode, this.vnode);
    this.vnode = newVNode;
  }
}

// Запуск застосунку
const root = document.getElementById("app")!;
new TodoApp(root);
