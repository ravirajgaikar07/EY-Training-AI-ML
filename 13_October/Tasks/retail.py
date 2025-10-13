import pandas as pd
# 1. Extract
products=pd.read_csv("products.csv")
orders=pd.read_csv("orders.csv")
customers=pd.read_csv("customers_2.csv")

# 2. Transform
# a. Join the datasets
df=pd.merge(orders,customers,on="CustomerID")
df=pd.merge(df,products,on="ProductID")

# b. Add new calculated columns:
df["TotalAmount"] = df["Quantity"] * df["Price"]
df["OrderDate"] = pd.to_datetime(df["OrderDate"])
df["OrderMonth"] = df["OrderDate"].dt.month

# c. Filter:
df=df[df["Quantity"]>=2]
df=df[(df["Country"]=="India") | (df["Country"]=="UAE")]

# d. Group and aggregate:
category_summary = df.groupby("Category",as_index=False)["TotalAmount"].sum()
segment_summary = df.groupby("Segment",as_index=False)["TotalAmount"].sum()

# e. Sorting & Ranking:
df=df.sort_values(by="TotalAmount", ascending=False)

# 3. Load

df.to_csv("processed_orders.csv",index=False)
category_summary.to_csv("category_summary.csv",index=False)
segment_summary.to_csv("segment_summary.csv",index=False)