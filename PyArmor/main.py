from secret_logic import secret_function
from utils import helper

def main():
    print("Start app")
    result = secret_function(5)
    print("Result:", result)
    helper()

if __name__ == "__main__":
    main()