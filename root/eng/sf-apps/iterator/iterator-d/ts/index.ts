class Node<T> {
  constructor(public value: T, public next: Node<T> | null = null) {}
}

class LinkedList<T> {
  private head: Node<T> | null = null;
  // методи додавання вузлів опущено

  iterator(): Iter<T> {
    let cursor = this.head;              // курсор-позиція живе В ітераторі
    return {
      hasNext: () => cursor !== null,
      next: () => {
        const v = cursor!.value;
        cursor = cursor!.next;           // крок по внутрішній структурі
        return v;
      },
    };
  }
}
