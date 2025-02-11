def greet(name):
    return f"Hello deployment, {name}!"

if __name__ == "__main__":
    name = input("Enter your name: ")
    print(greet(name))