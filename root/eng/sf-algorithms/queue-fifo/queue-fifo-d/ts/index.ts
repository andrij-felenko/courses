class Node<T> {
  next: Node<T> | null = null;   // наступний вузол у ланцюжку
  constructor(public value: T) {}
}

class Queue<T> {
  private head: Node<T> | null = null;  // звідки забирати
  private tail: Node<T> | null = null;  // куди чіпляти
  private size = 0;

  enqueue(value: T): void {      // покласти в хвіст
    const node = new Node(value);
    if (this.tail === null) this.head = node;   // була порожня
    else this.tail.next = node;
    this.tail = node;
    this.size++;
  }

  dequeue(): T {                 // забрати з голови
    if (this.head === null) throw new Error("черга порожня");
    const node = this.head;
    this.head = node.next;
    if (this.head === null) this.tail = null;   // зняли останній
    this.size--;
    return node.value;
  }
}
