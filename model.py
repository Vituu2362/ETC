from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

# User model
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)  # Max length 50
    password = Column(String(100), nullable=False)  # Storing hashed passwords, max length 100

    # Relationship to toll payments (or other related data)
    toll_payments = relationship('TollPayment', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)


# Toll Payment model
class TollPayment(Base):
    __tablename__ = 'toll_payments'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # Foreign key linking this toll payment to the user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<TollPayment {} for User {}>'.format(self.amount, self.user_id)