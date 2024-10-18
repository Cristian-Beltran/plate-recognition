
# services/user_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Vehicle, Base

class VehiclesService:
    def __init__(self, db_url='sqlite:///app.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_vehicle(self, plate, make, color, first_name, last_name, cellphone, ci, personal):
        session = self.Session()
        new_vehicle = Vehicle(make=make, color=color, plate=plate, first_name=first_name, last_name=last_name, cellphone=cellphone, ci=ci, personal=personal)
        session.add(new_vehicle)
        session.commit()
        session.close()
        return new_vehicle

    def get_vehicles(self):
        session = self.Session()
        vehicles = session.query(Vehicle).all()
        session.close()
        return vehicles

    def get_vehicle_by_id(self, vehicle_id):
        session = self.Session()
        vehicle = session.query(Vehicle).filter_by(plate=vehicle_id).first()
        session.close()
        return vehicle

    def update_vehicle(self, plate, make, color, first_name, last_name, cellphone, ci, personal):
        session = self.Session()
        vehicle = session.query(Vehicle).filter_by(plate=plate).first()
        vehicle.make = make
        vehicle.color = color
        vehicle.plate = plate
        vehicle.first_name = first_name
        vehicle.last_name = last_name
        vehicle.cellphone = cellphone
        vehicle.ci = ci
        vehicle.personal = personal
        session.commit()
        session.close()

    def get_last_vehicle(self):
        session = self.Session()
        vehicle = session.query(Vehicle).order_by(Vehicle.created_at.desc()).first()
        session.close()
        return vehicle

    def delete_vehicle(self, vehicle_id):
        session = self.Session()
        vehicle = session.query(Vehicle).filter_by(plate=vehicle_id).first()
        session.delete(vehicle)
        session.commit()
        session.close()
