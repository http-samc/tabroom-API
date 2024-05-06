def lprint(string: str):
    print(string)
    with open("logs.txt", "a") as f:
        f.write(string + "\n")
