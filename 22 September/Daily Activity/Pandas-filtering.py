import pandas as pd

data = {
    "Name": ["Abhishek", "Rahul", "Prathmesh", "Vinay"],
    "Age": [21,22,23,24],
    "Course": ["AI","ML","Cloud","CI/CD"],
    "Marks": [75,80,90,72]
}

df=pd.DataFrame(data)

print(df[df["Marks"]>75])