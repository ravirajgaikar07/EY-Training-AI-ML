import yaml
import logging

logging.basicConfig(
    filename="yaml_ops.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Logging started")
logging.info("Config Data")
configs = {
    "app": {
        "name": "Student Portal",
        "version": 1.0
    },
    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "root"
    }
}

logging.info("Saving config Data to YAML file")
with open("config.yaml", "w") as f:
    yaml.dump(configs, f)

logging.info("Loading the Data from YAML file")
try :
    with open("config.yaml", "r") as f:
        data=yaml.safe_load(f)
except FileNotFoundError as e:
    logging.error(f"file not found {e}")

print(data)

logging.info("Printing Database Connection String")
if data :
    print(f"Connecting to {data['database']['host']}:{data['database']['port']} as {data['database']['user']}")
else:
    logging.warning("NO data to show")

