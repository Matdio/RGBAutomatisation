from multiprocessing import Process, Queue
import random
import time

start = time.process_time()
n = 4

def rand_val(queue):
    list = []
    for i in range(300):
        num = random.random()
        list.append(num)
        if i%10 == 0:
            print(i)
    
    print("done")
    queue.put(list)


def main(n):
    results = []
    finishedProcesses = []
    queue = Queue()

    processes = [Process(target=rand_val, args=(queue,)) for _ in range(n)]

    for p in processes:
        p.start()
    
    for i    
    results = [queue.get() for _ in range(len(processes)+1)]
    print(results)

    for p in processes:
        p.join()


if __name__ == "__main__":
    main(n)
    
    
print(time.process_time() - start)  