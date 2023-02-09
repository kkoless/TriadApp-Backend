from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, )
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Boolean, default=False, nullable=False)


class Token(Base):
    __tablename__ = "tokens"
    access_token = Column(String, primary_key=True, nullable=False)
    expire_time = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


class Palette(Base):
    __tablename__ = "palettes"
    id = Column(Integer, primary_key=True, nullable=False)


class Color(Base):
    __tablename__ = "colors"
    id = Column(Integer, nullable=False, primary_key=True)
    hex = Column(String, nullable=False)
    name = Column(String, nullable=False)


class Palette_Color(Base):
    __tablename__ = "palettes_colors"
    id = Column(Integer, primary_key=True, nullable=False)
    palette_id = Column(Integer, ForeignKey('palettes.id'), nullable=False)
    color_id = Column(Integer, ForeignKey('colors.id'), nullable=False)


class User_Palette(Base):
    __tablename__ = "users_palettes"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    palette_id = Column(Integer, ForeignKey('palettes.id'), nullable=False)


class User_Color(Base):
    __tablename__ = "users_colors"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    color_id = Column(Integer, ForeignKey('colors.id'), nullable=False)
