from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import MainCategory, Base, SubCategory

app = Flask(__name__)

engine = create_engine('sqlite:///foodCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/categories/<int:mainCategory_id>/subcategories/JSON/')
def mainCategoryJSON(mainCategory_id):
    mainCategory = session.query(MainCategory).filter_by(id=mainCategory_id).one()
    subCategories = session.query(SubCategory).filter_by(
        mainCategory_id=mainCategory_id).all()
    return jsonify(SubCategory=[sc.serialize for sc in subCategories])



# ADD JSON ENDPOINT HERE
@app.route('/categories/<int:restaurant_id>/subcategories/JSON/')
def subCategoryJSON(mainCategory_id, subCategory_id):
    subCategory = session.query(SubCategory).filter_by(id=subCategory_id).one()
    return jsonify(SubCategory=subCategory.serialize)


# main categories & latest updates
@app.route('/')
@app.route('/latest_updates')
@app.route('/index')
@app.route('/categories')
def catalog_latest_updates():
    return "CatalogHome"


# sub categories of main category
# or main category clicked
@app.route('/categories/<int:mainCategory_id>/')
def mainCategory(mainCategory_id):
    return "category id = " + mainCategory_id


# sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/')
def subCategory(mainCategory_id, subCategory_id):
    return "sub category id = "+ subCategory_id +" in category id = " + mainCategory_id


# add new sub category
@app.route('/categories/<int:mainCategory_id>/new/',
           methods=['GET', 'POST'])
def newSubCategory(mainCategory_id):
    return "ADD new sub category in category id = " + mainCategory_id


# edit sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/edit/',
           methods=['GET', 'POST'])
def editSubCategory(mainCategory_id, subCategory_id):
    return "EDIT sub category id = "+ subCategory_id +" in category id = " + mainCategory_id


# delete sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/delete',
           methods=['GET', 'POST'])
def editSubCategory(mainCategory_id, subCategory_id):
    return "DELETE sub category id = "+ subCategory_id +" in category id = " + mainCategory_id

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
