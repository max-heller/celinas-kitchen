from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import text

from dbconfig import db
from formattingHelpers import forceNum, formatName, removeExcess, sortDict
from hardcodedShit import clientTypes


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    hash = db.Column(db.Text)

    def __init__(self, request):
        self.name = formatName(request.form.get("name"))
        self.hash = pwd_context.hash(request.form.get("password"))

        # make sure admin with same name doesn't already exist
        if not Admin.query.filter_by(name=self.name).first():
            db.session.add(self)
            db.session.commit()

    def update(self, request):
        if not pwd_context.verify(request.form.get("password_old"), self.hash):
            return False
        self.hash = pwd_context.hash(request.form.get("password"))
        db.session.commit()
        return True

    def check(request):
        name = formatName(request.form.get("name"))
        admin = Admin.query.filter_by(name=name).first()
        if admin is None or not pwd_context.verify(request.form.get("password"), admin.hash):
            return None
        return admin.id


class BaseClient(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(10))
    clientType = db.Column(db.Integer)
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Text)
    generalNotes = db.Column(db.Text)
    dietaryPreferences = db.Column(db.Text)

    def __init__(self, request, clientType=0):
        self.name = formatName(request.form.get("name"))
        self.phone = removeExcess(request.form.get("phone"))
        self.clientType = clientType
        self.address = request.form.get("address").lower()
        self.delivery = forceNum(request.form.get("delivery"))
        self.allergies = request.form.get("allergies").lower()
        self.generalNotes = request.form.get("generalNotes")
        self.dietaryPreferences = request.form.get("dietaryPreferences")

    def update(self, request):
        self.__init__(request, self.clientType)

    def toDict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def baseClient(request, clientType=0):
    name = formatName(request.form.get("name"))
    client = BaseClient.query.filter_by(name=name).first()
    if client:
        client.update(request)
    else:
        client = BaseClient(request, clientType)
        db.session.add(client)
    db.session.commit()
    return client.id


class StandingOrderClient(db.Model):
    __tablename__ = "standingOrder"
    id = db.Column(db.Integer, primary_key=True)
    protein = db.Column(db.Text)
    saladDislikes = db.Column(db.Text)
    saladLoves = db.Column(db.Text)
    hotplateLikes = db.Column(db.Text)
    hotplateDislikes = db.Column(db.Text)
    hotplateLoves = db.Column(db.Text)
    weeklyMoney = db.Column(db.Integer)
    mondaySalads = db.Column(db.Integer)
    thursdaySalads = db.Column(db.Integer)
    saladDressings = db.Column(db.Boolean, default=False)
    mondayHotplates = db.Column(db.Integer)
    tuesdayHotplates = db.Column(db.Integer)
    thursdayHotplates = db.Column(db.Integer)
    saladNotes = db.Column(db.Text)
    hotplateNotes = db.Column(db.Text)

    def __init__(self, request, clientId):
        self.id = clientId
        self.protein = request.form.get("protein").lower()
        self.saladDislikes = request.form.get("saladDislikes").lower()
        self.saladLoves = request.form.get("saladLoves").lower()
        self.saladDressings = forceNum(request.form.get("saladDressings"))
        self.hotplateLikes = request.form.get("hotplateLikes").lower()
        self.hotplateDislikes = request.form.get("hotplateDislikes").lower()
        self.hotplateLoves = request.form.get("hotplateLoves").lower()
        self.weeklyMoney = forceNum(request.form.get("weeklyMoney"))
        self.mondaySalads = forceNum(request.form.get("mondaySalads"))
        self.thursdaySalads = forceNum(request.form.get("thursdaySalads"))
        self.mondayHotplates = forceNum(request.form.get("mondayHotplates"))
        self.tuesdayHotplates = forceNum(request.form.get("tuesdayHotplates"))
        self.thursdayHotplates = forceNum(request.form.get("thursdayHotplates"))
        self.saladNotes = request.form.get("saladNotes")
        self.hotplateNotes = request.form.get("hotplateNotes")

    def update(self, request):
        self.__init__(request, self.id)

    def toDict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def standingOrderClient(request):
    clientId = baseClient(request, 1)
    client = StandingOrderClient.query.get(clientId)
    if client:
        client.update(request)
    else:
        client = StandingOrderClient(request, clientId)
        db.session.add(client)
    db.session.commit()


def deleteClient(name):
    tableNames = {0: "clients", 1: "standingOrder"}
    clientId = BaseClient.query.filter_by(name=formatName(name)).first().id
    clientType = BaseClient.query.get(clientId).clientType
    t = text("DELETE FROM clients WHERE id=:clientId")
    db.engine.execute(t, clientId=clientId)
    if clientType != 0:
        table = tableNames[clientType]
        t = text("DELETE FROM {table} WHERE id=:clientId".format(table=table))
        db.engine.execute(t, clientId=clientId)
    db.session.commit()


def getClient(name):
    """
    Input: name
    Returns: associated client details as a sorted dictionary, or None if no client exists
    """
    tableNames = {0: "clients", 1: "standingOrder"}
    try:
        name = formatName(name)
        t = text("SELECT * FROM clients WHERE name LIKE :name")
        client = db.engine.execute(t, name=name).first()
        if client["clientType"] != 0:
            table = tableNames[client["clientType"]]
            t = text(
                "SELECT * FROM {table} JOIN clients ON {table}.id = clients.id WHERE name LIKE :name".format(table=table))
            client = db.engine.execute(t, name=name).first()
        return sortDict(client, "clientAttributes")
    except:
        return None


clientTypes = sortDict(clientTypes, dictName="clientTypes")
