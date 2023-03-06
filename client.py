import requests


if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2 or argv[1] not in ["post", "get"]:
        raise ValueError("Not enough params. Usage: python client.py post message. OR python client.py get")
    url = "http://127.0.0.1:8080/"
    if argv[1] == "post":
        msg = " ".join(argv[2:])
        data = {"message": msg}
        try:
            requests.post(url = url, data = data)
        except:
            print(f"Error connecting {url}")
    else:
        try:
            r = requests.get(url)
            print(r.text)
        except:
            print(f"Error connecting to {url}")
