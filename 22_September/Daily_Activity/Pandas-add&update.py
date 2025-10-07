import pandas as pd
import numpy as np

data = {
    "Name": ["Abhishek", "Rahul", "Prathmesh", "Vinay"],
    "Age": [21,22,23,24],
    "Course": ["AI","ML","Cloud","CI/CD"],
    "Marks": [60,80,90,72]
}

df=pd.DataFrame(data)

df["Result"]=np.where(df["Marks"]>=70,"Pass","Fail")
df.loc[df["Name"]=="Rahul","Marks"]=90

print(df)
