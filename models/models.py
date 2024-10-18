from sqlalchemy import Column, Integer, String, Float,DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name= Column(String)
    last_name = Column(String)
    ci = Column(String )
    cellphone = Column(String)
    role = Column(String, nullable=False, default="Operador")
    last_login = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.now)
    def __repr__(self):
        return f"<User(id={self.id}, first_name={self.first_name}, email={self.email}, role={self.role})>"


class Vehicle(Base):
    __tablename__ = 'vehicles'
    plate = Column(String(30), primary_key=True)
    make = Column(String(50), nullable=False)
    color = Column(String(30))
    status = Column(String(30), default="Fuera")

    first_name= Column(String(30))
    last_name= Column(String(30))
    cellphone = Column(String(30))
    ci = Column(String(30))
    personal = Column(String(30), default="Estudiante")
    histories = relationship('History', back_populates='vehicle')
    created_at = Column(DateTime, default=datetime.now)
    def __repr__(self):
        return f"<Vehicle(make='{self.make}', model='{self.model}', plate={self.plate}, driver={self.driver})>"

class History(Base):
    __tablename__ = 'histories'
    id = Column(Integer, primary_key=True)
    plate = Column(String(30),ForeignKey("vehicles.plate"), nullable=False)
    authorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    vehicle = relationship("Vehicle", back_populates="histories")
    type = Column(String(30), default="Entrada")
    def __repr__(self):
        return '<History(id=%r, plate=%r, created_at=%r)>' % (self.id, self.plate, self.created_at)
