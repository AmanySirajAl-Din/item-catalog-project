import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class mainCategory(Base):
    

class subCategory(Base):


engine = create_engine('sqlite:///foodCatalog.db')
Base.metadata.create_all(engine)