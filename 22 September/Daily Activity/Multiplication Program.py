# Multiplication Program

def multiplication_table(num):
    print(f"Multiplication Table of {num}")
    for i in range(1,11):
        print(f"{num} x {i} = {num*i}")

num=int(input("Enter Your Number : "))
multiplication_table(num)