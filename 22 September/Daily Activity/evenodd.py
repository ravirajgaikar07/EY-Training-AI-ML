# EvenOdd Program

def check_evenodd(num):
    if num%2==0:
        return "Even"
    else :
        return "Odd"

num=int(input("Enter Your Number : "))
answer=check_evenodd(num)
print(f"Number is {answer}")