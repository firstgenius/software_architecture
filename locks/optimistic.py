import hazelcast as hz

from sys import argv
from time import sleep


if __name__ == '__main__':
    try:
        proc = argv[1]
    except:
        print("Wrong usage. Please, specify process id in terminal")


    client = hz.HazelcastClient()
    hz_map = client.get_map("map")
    key = "2"

    hz_map.put_if_absent(key, 0).result()

    for i in range(50):
        while True:
            oldValue = hz_map.get(key).result()
            sleep(0.001)
            newValue = oldValue + 1
            if hz_map.replace_if_same(key, oldValue, newValue).result():
                break

    last_worker_value = hz_map.get(key).result()

    print(f"Worker {proc} got {last_worker_value}")
    client.shutdown()
