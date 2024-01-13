

def my_decorator(f):
    def wrapper():
        print("entering")
        f()
        print("leaving")
    return wrapper


@my_decorator
def poopie():
    print("POOP")


if __name__ == "__main__":
    poopie()
