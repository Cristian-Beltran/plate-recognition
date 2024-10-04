# services/user_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import User, Base

class UserService:
    def __init__(self, db_url='sqlite:///app.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_user(self, username, password, fullname, role):
        session = self.Session()
        new_user = User(username=username, password=password, fullname=fullname, role=role)
        session.add(new_user)
        session.commit()
        session.close()
        return new_user

    def get_user(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user

    def get_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def update_user(self, user_id, username=None, password=None, fullname=None, role=None):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            if username:
                user.username = username
            if password:
                user.password = password
            if fullname:
                user.fullname = fullname
            if role:
                user.role = role

            session.commit()
        session.close()
        return user

    def delete_user(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
        session.close()
        return user

    def login(self, username, password):
        session = self.Session()
        user = session.query(User).filter(User.username == username).first()
        if user and user.password == password:
            session.close()
            return user
        else:
            session.close()
            return None
