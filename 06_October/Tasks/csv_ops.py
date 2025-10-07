import pandas as pd
import logging

logging.basicConfig(
    filename="csv_ops.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("CSV Data")
data = {
    "product" : ["Laptop", "Mouse", "Keyboard"],
    "price" : [70000, 500, 1200],
    "quantity" : [2, 5, 3]
}
logging.info("Creating DataFrame")
df = pd.DataFrame(data)
logging.info("Creating CSV")
df.to_csv("output.csv", index=False)

logging.info("Loading CSV")
try:
    df=pd.read_csv("output.csv")
except FileNotFoundError:
    logging.error("Missing File")

logging.info("Loading CSV")
try :
    df["total_sales"]=df["price"]*df["quantity"]
except ValueError as e:
    logging.error(e)
logging.info("printing total sales")
print(df[["product","total_sales"]])

for _,row in df.iterrows():
    logging.info(f"Product : {row['product']} | Total Sales : {row['total_sales']}")


