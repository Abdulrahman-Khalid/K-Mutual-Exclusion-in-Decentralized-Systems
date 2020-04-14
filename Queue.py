class Queue:
    def __init__(self, queue=[]):
        self.queue = queue

    def enqueue(self, element):
        self.queue.append(element)

    def dequeue(self):
        return self.queue.pop(0)

    def front(self):
        return queue[0]

    def rear(self):
        return queue[-1]

    def is_empty(self):
        return len(self.queue) == 0

    def remove(self, element):
        self.queue.remove(element)

    def copy(self):
        return self.queue.copy()

    def size(self):
        return len(self.queue)