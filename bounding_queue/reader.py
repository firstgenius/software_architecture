import hazelcast as hz

from sys import argv
from time import sleep


if __name__ == '__main__':
    try:
        proc = argv[1]
    except:
        print("Wrong usage. Please, specify process id in terminal")


    client = hz.HazelcastClient()
    queue = client.get_queue("queue")

    while True:
        value = queue.poll().result()
        if value is None:
            continue
        print(f"Reader worker {proc} polled {value} value out of the queue.")
