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

    for _ in range(50):
        hz_map.lock(key).result()
        try:
            value = hz_map.get(key).result()
            sleep(0.01)
            value += 1
            hz_map.put(key, value).result()
        finally:
            hz_map.unlock(key).result()

    last_worker_value = hz_map.get(key).result()

    print(f"Worker {proc} got {last_worker_value}")
    client.shutdown()
