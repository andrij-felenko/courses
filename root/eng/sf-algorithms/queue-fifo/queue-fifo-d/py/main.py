class Node:
    def __init__(self, value):
        self.value = value
        self.next = None          # наступний вузол у ланцюжку

class Queue:
    def __init__(self):
        self.head = None          # звідки забирати (найстаріший)
        self.tail = None          # куди чіпляти (найновіший)
        self.size = 0

    def enqueue(self, value):     # покласти в хвіст
        node = Node(value)
        if self.tail is None:     # черга була порожня
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1

    def dequeue(self):            # забрати з голови
        if self.head is None:
            raise IndexError("черга порожня")
        node = self.head
        self.head = node.next
        if self.head is None:     # зняли останній — хвоста більше нема
            self.tail = None
        self.size -= 1
        return node.value
