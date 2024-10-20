# services/user_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import User, Base
import datetime
import os

class UserService:
    def __init__(self, db_url='sqlite:///app.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_user(self, email, password, first_name,last_name, ci, cellphone, role):
        session = self.Session()
        new_user = User(email=email, password=password, first_name=first_name, last_name=last_name, ci=ci, cellphone=cellphone, role=role)
        session.add(new_user)
        session.commit()
        session.close()
        return new_user

    def get_last_user(self):
        session = self.Session()
        user = session.query(User).order_by(User.created_at.desc()).first()
        session.close()
        return user

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

    def update_user(self, user_id, email=None, password=None, first_name=None, last_name=None, ci=None, cellphone=None, role=None):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            if email:
                user.email = email
            if password:
                user.password = password
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if ci:
                user.ci = ci
            if cellphone:
                user.cellphone = cellphone
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

    def add_last_login(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.datetime.now()
            session.commit()
        session.close()

    def login(self, email, password):
        session = self.Session()
        user = session.query(User).filter(User.email == email).first()
        if(user and password == user.password):
            return user
        session.close()
        return None

    def reset_password(self, email, password):
        session = self.Session()
        user = session.query(User).filter(User.email == email).first()
        if user:
            user.password = password
            session.commit()
        session.close()

    def get_user_email(self, email):
        session = self.Session()
        user = session.query(User).filter(User.email == email).first()
        session.close()
        return user
