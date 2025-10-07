import yaml

model={
    "model" : "RandomForest",
    "params" : {
        "n_estimators": 100,
        "max_depth" : 5
    },
    "dataset" : "students.csv"
}

with open ("models.yaml","w") as f:
    yaml.dump(model,f)

with open ("models.yaml","r") as f:
    data=yaml.safe_load(f)

print(data["params"]["n_estimators"])