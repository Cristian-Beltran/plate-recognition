from sqlalchemy import Column, Integer, String, Float,DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    fullname = Column(String, nullable=False)
    role = Column(String, nullable=False, default="Usuario")
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.passowrd}, fullname={self.fullname}, role={self.role})>"


class Vehicle(Base):
    __tablename__ = 'vehicles'
    plate = Column(String(30), primary_key=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(30))

    driver = Column(String(30))
    cellphone = Column(String(30))
    license = Column(String(30))
    histories = relationship('History', back_populates='vehicle')
    def __repr__(self):
        return f"<Vehicle(make='{self.make}', model='{self.model}', plate={self.plate}, driver={self.driver})>"

class History(Base):
    __tablename__ = 'histories'
    id = Column(Integer, primary_key=True)
    plate = Column(String(30),ForeignKey("vehicles.plate"), nullable=False)
    authorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicle = relationship("Vehicle", back_populates="histories")
    def __repr__(self):
        return '<History(id=%r, plate=%r, created_at=%r)>' % (self.id, self.plate, self.created_at)
