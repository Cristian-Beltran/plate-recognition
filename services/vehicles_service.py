
# services/user_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Vehicle, Base

class VehiclesService:
    def __init__(self, db_url='sqlite:///app.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_vehicle(self, make, model, year, color, plate, driver, cellphone, license):
        session = self.Session()
        new_vehicle = Vehicle(make=make, model=model, year=year, color=color, plate=plate, driver=driver, cellphone=cellphone, license=license)
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

    def update_vehicle(self, vehicle_id, make, model, year, color, plate, driver, cellphone, license):
        session = self.Session()
        vehicle = session.query(Vehicle).filter_by(plate=vehicle_id).first()
        vehicle.make = make
        vehicle.model = model
        vehicle.year = year
        vehicle.color = color
        vehicle.plate = plate
        vehicle.driver = driver
        vehicle.cellphone = cellphone
        vehicle.license = license
        session.commit()
        session.close()

    def delete_vehicle(self, vehicle_id):
        session = self.Session()
        vehicle = session.query(Vehicle).filter_by(plate=vehicle_id).first()
        session.delete(vehicle)
        session.commit()
        session.close()
