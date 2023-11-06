from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Attraction(db.Model):
    pass

class Mrt(db.Model):
    pass

class Category(db.Model):
    pass

class Image(db.Model):
    pass

class Mmeber(db.Model):
    pass

class Book(db.Model):
    pass


# TODO
# Add function to get/add data into table