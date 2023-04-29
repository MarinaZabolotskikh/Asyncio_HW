from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

PG_DSN = 'postgresql+asyncpg://user:1234@127.0.0.1:5431/asynciohw'

engine = create_async_engine(PG_DSN)


class Base(DeclarativeBase):
    pass


class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, autoincrement=True)
    birth_year = Column(String)
    eye_color = Column(String)
    films = Column(Text)
    gender = Column(String)
    hair_color = Column(String)
    height = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    name = Column(String)
    skin_color = Column(Text)
    species = Column(Text)
    vehicles = Column(Text)


Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
