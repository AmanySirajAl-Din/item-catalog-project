from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import MainCategory, Base, SubCategory

app = Flask(__name__)

engine = create_engine('sqlite:///foodCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# main categories & last updates
@app.route('/')
@app.route('/last_update')
@app.route('/index')
@app.route('/categories')
def catalog_lasts_update():
    return "CatalogHome"


# sub categories of main category
# or main category clicked
@app.route('/categories/<int:mainCategory_id>/')
def CatalogHome(mainCategory_id):
    return "category id = " + mainCategory_id


# sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/')
def newMenuItem(mainCategory_id, subCategory_id):
    return "sub category id = "+ subCategory_id +" in category id = " + mainCategory_id


# add new sub category
@app.route('/categories/<int:mainCategory_id>/new/',
           methods=['GET', 'POST'])
def newMenuItem(mainCategory_id):
    return "ADD new sub category in category id = " + mainCategory_id


# edit sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(mainCategory_id, subCategory_id):
    return "EDIT sub category id = "+ subCategory_id +" in category id = " + mainCategory_id


# delete sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/delete',
           methods=['GET', 'POST'])
def editMenuItem(mainCategory_id, subCategory_id):
    return "DELETE sub category id = "+ subCategory_id +" in category id = " + mainCategory_id

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
