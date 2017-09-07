from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///foodCatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# data source from wiki and allrecipes.com

# Healthy food category
foodCategory1 = mainCategory(name="Healthy", description="A healthy diet is one that helps to maintain or improve overall health.")

session.add(foodCategory1)
session.commit()

foodItem1 = subCategory(name="Diabetic", description="Diabetic-friendly cakes, cookies, and more low-sugar desserts, plus dinner ideas.", category=foodCategory1)

session.add(foodItem1)
session.commit()

foodItem1 = subCategory(name="Gluten-Free", description="Recipes that strictly excludes gluten, a mixture of proteins found in wheat and related grains, including barley, rye, oat, and all their species and hybrids.", category=foodCategory1)

session.add(foodItem1)
session.commit()

foodItem1 = subCategory(name="Low-Sodium", description="According to the Mayo Clinic, a low-sodium recipe is one with no more than 140 milligrams of sodium per serving.", category=foodCategory1)

session.add(foodItem1)
session.commit()

foodItem1 = subCategory(name="Low-fat", description="Recipes that restricts fat and often saturated fat and cholesterol as well. Low-fat diets are intended to reduce diseases such as heart disease and obesity.", category=foodCategory1)

session.add(foodItem1)
session.commit()




print "added food categories!"