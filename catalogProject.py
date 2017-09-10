from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import MainCategory, Base, SubCategory

#1- NEW imports
from flask import session as login_session
import random, string

# Connect to Database and create database session
engine = create_engine('sqlite:///foodCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# JSON APIs to view Restaurant Information
@app.route('/categories/maincategories/JSON/')
def CategoriesJSON():
    mainCategories = session.query(MainCategory).all()
    return jsonify(MainCategory=[mc.serialize for mc in mainCategories])


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
    mainCategories = session.query(MainCategory).order_by(asc(MainCategory.name))
    latestItems = session.query(SubCategory).order_by(desc(SubCategory.id)).limit(7)
    return render_template('catalog.html', mainCategories=mainCategories, latestItems=latestItems)


# sub categories of main category
# or main category clicked
@app.route('/categories/<int:mainCategory_id>/')
def mainCategory(mainCategory_id):
    mainCategories = session.query(MainCategory).order_by(asc(MainCategory.name))
    mainCategory = session.query(MainCategory).filter_by(id=mainCategory_id).one()
    subCategories = session.query(SubCategory).filter_by(mainCategory_id=mainCategory_id).order_by(asc(SubCategory.name))
    return render_template(
        'food_main_category.html', mainCategory=mainCategory, mainCategory_id=mainCategory_id, subCategories=subCategories)


# sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/')
def subCategory(mainCategory_id, subCategory_id):
    mainCategories = session.query(MainCategory).order_by(asc(MainCategory.name))
    subCategory = session.query(SubCategory).filter_by(subCategory_id=subCategory_id).one()
    return render_template('food_sub_category.html', subCategory_id=subCategory_id, subCategory=subCategory)


# add new sub category
@app.route('/categories/<int:mainCategory_id>/new/',
           methods=['GET', 'POST'])
def newSubCategory(mainCategory_id):
    if request.method == 'POST':
        newItem = SubCategory(name=request.form['name'], description=request.form[
                           'description'], mainCategory_id=mainCategory_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalog_latest_updates'))
    else:
        return render_template('new_subCtegory.html', mainCategory_id=mainCategory_id)


# edit sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/edit/',
           methods=['GET', 'POST'])
def editSubCategory(mainCategory_id, subCategory_id):
    editedItem = session.query(SubCategory).filter_by(id=subCategory_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('catalog_latest_updates'))
    else:
        return render_template(
            'edit_subCategory.html', mainCategory_id=mainCategory_id, subCategory_id=subCategory_id, item=editedItem)


# delete sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/delete/',
           methods=['GET', 'POST'])
def deleteSubCategory(mainCategory_id, subCategory_id):
    itemToDelete = session.query(MenuItem).filter_by(id=subCategory_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('catalog_latest_updates'))
    else:
        return render_template(
            'delete_subCategory.html', mainCategory_id=mainCategory_id, subCategory_id=subCategory_id, item=itemToDelete)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
