from mongoengine import *

connect('applab')


class User(Document):
    id = StringField(primary_key=True)


class Experiment(Document):
    name = StringField(unique=True)
    excluded_users = ListField(ReferenceField(User))
    variant_choice = StringField(default="remember")


class Variant(Document):
    experiment = ReferenceField(Experiment)
    name = StringField()
    data = DynamicField()
    users = ListField(ReferenceField(User))
    successes = IntField(default=0)
    trials = IntField(default=0)
