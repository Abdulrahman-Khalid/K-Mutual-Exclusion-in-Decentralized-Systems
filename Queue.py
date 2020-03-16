class Queue:
    def __init__(self, queue=[]):
        self.queue = queue

    def push(self, element):
        self.queue.append(element)

    def pop(self):
        return self.queue.pop()

    def front(self):
        return queue[-1]

    def rear(self):
        return queue[0]

    def is_empty(self):
        return len(self.queue) == 0

    def remove(self, element):
        self.queue.remove(element)
