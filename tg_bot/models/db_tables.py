from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """
    A table with users and their main parameters
    """
    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True)
    user_id = Column(Integer, primary_key=True,)
    user_name = Column(String)
    all_photos = relationship('UserFavoritePhotos', back_populates='user',
                          cascade="all, delete-orphan")


class UserFavoritePhotos(Base):
    """
    A table with viewed photos of users and their main parameters
    """
    __tablename__ = 'user_photos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    relation_user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    user = relationship('User', back_populates='all_photos')
    photo_url = Column(String)