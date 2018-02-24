import os

clientTypes = {"Base": 0, "Standing Order": 1}
clientAttributeOrder = ["id", "clientType", "name", "phone", "address", "hash", "delivery", "dietaryPreferences", "mondaySalads", "thursdaySalads", "weeklySoups", "weeklyHotplates",
                        "allergies", "protein", "saladDislikes", "saladLoves", "saladDressings", "hotplateLikes", "hotplateDislikes", "hotplateLoves",
                        "generalNotes", "saladNotes", "generalNotes", "hotplateNotes"]
clientTypeOrder = ["Base", "Standing Order"]
clientAttributes = {}
clientAttributes[0] = ["name", "phone",
                       "address", "allergies", "dietaryPreferences", "generalNotes", "delivery"]
saladServiceAttributes = ["mondaySalads", "thursdaySalads", "allergies","protein", "saladDislikes", "saladLoves", "saladDressings", "saladNotes"]
clientAttributes[1] = sorted(clientAttributes[0] + ["mondaySalads", "thursdaySalads", "protein", "saladDislikes", "saladLoves", "saladDressings", "saladNotes",
                                                    "hotplateLikes", "hotplateDislikes", "hotplateLoves", "hotplateNotes", "weeklyHotplates", "weeklySoups"],
                             key=lambda x: clientAttributeOrder.index(x))
inputTypes = {
    "defaultText": ["name", "phone", "address", "mondaySalads", "thursdaySalads", "weeklyHotplates", "weeklySoups", "saladDressings", "delivery"],
    "opinionText": ["protein", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "allergies", "dietaryPreferences"],
    "noteText": ["generalNotes", "saladNotes", "hotplateNotes"]
}
try:
    dbConfig = "mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(username=os.environ["RDS_USERNAME"],
                                                                                   password=os.environ["RDS_PASSWORD"],
                                                                                   server=os.environ["RDS_HOSTNAME"],
                                                                                   port=os.environ["RDS_PORT"],
                                                                                   db=os.environ["RDS_DB_NAME"])
except:
    dbConfig = "mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(
        username="admin", password="y94D6NDeTColiQDZAEWp", server="aa13t6f8mueycaj.cy9bm4pmzdu7.us-east-1.rds.amazonaws.com", port="3306", db="ebdb")
