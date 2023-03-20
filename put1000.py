import hazelcast as hz


if __name__ == '__main__':
    client = hz.HazelcastClient()
    m = client.get_map("m1").blocking()

    for i in range(1000):
        m.put(i, f"Item value: {i}")

    print("Successfully put 1000 values to map")

    client.shutdown()
    
