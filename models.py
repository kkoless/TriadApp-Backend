from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Boolean, default=False, nullable=False)


class Token(Base):
    __tablename__ = "tokens"
    access_token = Column(String, primary_key=True, nullable=False)
    expire_time = Column(String, nullable=False)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)


class Palette(Base):
    __tablename__ = "palettes"
    id = Column(Integer, primary_key=True, nullable=False)


class Color(Base):
    __tablename__ = "colors"
    id = Column(Integer, nullable=False, primary_key=True)
    hex = Column(String, nullable=False)
    name = Column(String, nullable=False)
    alpha = Column(Float, nullable=False)


class Palette_Color(Base):
    __tablename__ = "palettes_colors"
    id = Column(Integer, primary_key=True, nullable=False)
    palette_id = Column(Integer, ForeignKey('palettes.id', ondelete='CASCADE'), nullable=False)
    color_id = Column(Integer, ForeignKey('colors.id', ondelete='CASCADE'), nullable=False)


class User_Palette(Base):
    __tablename__ = "users_palettes"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    palette_id = Column(Integer, ForeignKey('palettes.id', ondelete='CASCADE'), nullable=False)


class User_Color(Base):
    __tablename__ = "users_colors"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    color_id = Column(Integer, ForeignKey('colors.id', ondelete='CASCADE'), nullable=False)
