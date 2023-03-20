import hazelcast as hz

if __name__ == '__main__':

    client = hz.HazelcastClient()
    queue = client.get_queue("queue").blocking()
    queue.clear()

    number = 0
    while True:
        print(f"Pushing number {number} to the queue by producer")
        queue.put(number)
        number += 1

