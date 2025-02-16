from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import os
import bcrypt


db = SQLAlchemy()



#class for a user
class User(db.Model):
    #name of model
    __tablename__ = "user"
    #columns
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    targetDate = db.Column(db.DateTime, nullable=False) #the day they will lose the weight. 
    


    #nutrient data about the person. 
    calories = db.Column(db.Integer, nullable=False)
    potassium = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    totalfat = db.Column(db.Integer, nullable=False)


    max_daily_calories = db.Column(db.Integer, nullable=False)
    max_daily_protein = db.Column(db.Integer, nullable=False)

    #now we need to initialize this object
    #initialize:
    def __init__(self, **kwargs):
        """
        initialize an assignment object
        """
        self.age = kwargs.get('age')
        self.gender = kwargs.get('gender')
        self.weight = kwargs.get('weight')
        self.height = kwargs.get('height')
        self.goal = kwargs.get('goal')
        self.targetDate = kwargs.get('targetDate')



    #serialize method
    def serialize(self):
        return{
            "id": self.id,
            "age": self.id,
            "weight": self.weight,
            "gender": self.age,
            "height": self.profilePictureUrl,
            "goal": self.starbucksLocation,
            "targetDate": self.targetDate
        }
    

    #return nutrient data
    def serialize(self):
        return{
            "calories": self.calories,
            "potassium": self.potassium,
            "protein": self.protein,
            "carbs": self.carbs,
            "totalfat": self.totalfat
        }


    

