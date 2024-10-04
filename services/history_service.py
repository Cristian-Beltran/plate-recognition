from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Vehicle, History, Base
from datetime import datetime
import base64
import os
from PIL import Image
import io

class HistoryService:
    def __init__(self, db_url='sqlite:///app.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_history(self, plate, image):
        session = self.Session()
        vehicle = session.query(Vehicle).filter(Vehicle.plate == plate).first()
        if vehicle:
            new_history = History(plate=plate, authorized=True)
        else:
            new_history = History(plate=plate)

        session.add(new_history)
        session.commit()
        # Create folder and save image
        folder_name = "history_images"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        image_filename = f"{new_history.id}.jpg"
        image_path = os.path.join(folder_name, image_filename)
        # Convert image to PIL Image and save
        img_bytes = base64.b64decode(image)
        img = Image.open(io.BytesIO(img_bytes))
        img.save(image_path)
        session.close()
        return new_history

    def get_history_image(self, id):
        if not os.path.exists("history_images"):
            return None
        image_filename = f"{id}.jpg"
        image_path = os.path.join("history_images", image_filename)
        if os.path.exists(image_path):
            image = open(image_path, "rb")
            image_base64 = base64.b64encode(image.read())
            image.close()
            return image_base64.decode('utf-8')
        else:
            return None

    def get_history(self, plate):
        session = self.Session()
        history = session.query(History).filter(History.plate == plate).first()
        history.image = self.get_history_image(history.id)
        session.close()
        return history

    def get_histories_autorized(self):
        session = self.Session()
        histories = session.query(History).filter(History.authorized == True).all()
        for history in histories:
            history.image = self.get_history_image(history.id)
        return histories

    def get_histories_not_autorized(self):
        session = self.Session()
        histories = session.query(History).filter(History.authorized == False).all()
        for history in histories:
            history.image = self.get_history_image(history.id)
        return histories

    def get_histories_today(self):
        session = self.Session()
        histories = session.query(History).filter(History.created_at >= datetime.now()).all()
        for history in histories:
            history.image = self.get_history_image(history.id)
        return histories

    def get_last_history(self):
        session = self.Session()
        history = session.query(History).order_by(History.created_at.desc()).first()
        history.image = self.get_history_image(history.id)
        session.close()
        return history
