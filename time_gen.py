import time

def run_clock(duration,queue):
    start_time = time.time()

    while time.time() - start_time < duration:
        current_time = time.time() - start_time
        # print(f"Time elapsed: {current_time:.2f} seconds")
        time.sleep(1)  # Pause for 1 
        
    ## send mail 
    # print("after 10 sec ")

    print(f"Clock has run for {duration} ")

    print(f"Send mail to: {queue.front.name if queue.front else None}")


# # run_clock(10)

class QueueNode:
    def __init__(self, name, estimated_time):
        self.name = name
        self.estimated_time = estimated_time
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None

    def is_empty(self):
        return self.front is None

    def enqueue(self, name, estimated_time):
        new_node = QueueNode(name, estimated_time)
        if self.is_empty():
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node

    def dequeue(self):
        if self.is_empty():
            return None
        else:
            removed_node = self.front
            self.front = self.front.next
            if self.front is None:
                self.rear = None
            return removed_node

if __name__ == "__main__":
    # Example usage:
    queue = Queue()

    # Enqueue some items
    queue.enqueue("Ani", 4)  # Starting with 0 estimated_time
    queue.enqueue("Swa", 4)
    queue.enqueue("Sai", 3)
    queue.enqueue("prat", 4)
    queue.enqueue("priya", 6)



    # Process tasks and run the clock
    while not queue.is_empty():
        task = queue.dequeue()
        # print(f"Processing {task.name} with estimated time {task.estimated_time} seconds.")
        # print(queue.front.name)

        curr_time = task.estimated_time
        run_clock(curr_time,queue)
