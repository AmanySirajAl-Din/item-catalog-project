# 1- Configuration code begining
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# 3- Class code
class mainCategory(Base):
    

class subCategory(Base):

    
    
# 2- Configuration code ending
engine = create_engine('sqlite:///foodCatalog.db')
Base.metadata.create_all(engine)