from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import MainCategory, Base, SubCategory

#1- NEW imports
from flask import session as login_session
import random, string

# 3- imports for Gconnect method
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# 4- declare CLIENT_ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

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


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    
    
    
# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    
    
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
        'food_main_category.html', mainCategories=mainCategories, mainCategory=mainCategory, mainCategory_id=mainCategory_id, subCategories=subCategories)


# sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/')
def subCategory(mainCategory_id, subCategory_id):
    mainCategories = session.query(MainCategory).order_by(asc(MainCategory.name))
    subCategory = session.query(SubCategory).filter_by(id=subCategory_id).one()
    return render_template('food_sub_category.html', subCategory_id=subCategory_id, subCategory=subCategory)


# add new sub category
@app.route('/categories/<int:mainCategory_id>/new/',
           methods=['GET', 'POST'])
def newSubCategory(mainCategory_id):
    # chech if user loogged in or not
    # to protect praivate pages from access
    if 'username' not in login_session:
        return redirect('/login')
    
    if request.method == 'POST':
        newItem = SubCategory(name=request.form['name'], description=request.form[
                           'description'], mainCategory_id=mainCategory_id)
        session.add(newItem)
        session.commit()
        flash("New food sub category item created!")
        return redirect(url_for('catalog_latest_updates'))
    else:
        return render_template('new_subCtegory.html', mainCategory_id=mainCategory_id)


# edit sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/edit/',
           methods=['GET', 'POST'])
def editSubCategory(mainCategory_id, subCategory_id):
    # chech if user loogged in or not
    # to protect praivate pages from access
    if 'username' not in login_session:
        return redirect('/login')
    
    editedItem = session.query(SubCategory).filter_by(id=subCategory_id).one()
    editedItemName = editedItem.name
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("The " + editedItemName + " (food sub category) has been edited")
        return redirect(url_for('catalog_latest_updates'))
    else:
        return render_template(
            'edit_subCategory.html', mainCategory_id=mainCategory_id, subCategory_id=subCategory_id, item=editedItem)
    
    
# delete sub category
@app.route('/categories/<int:mainCategory_id>/<int:subCategory_id>/delete/',
           methods=['GET', 'POST'])
def deleteSubCategory(mainCategory_id, subCategory_id):
    # chech if user loogged in or not
    # to protect praivate pages from access
    if 'username' not in login_session:
        return redirect('/login')
    
    itemToDelete = session.query(MenuItem).filter_by(id=subCategory_id).one()
    itemToDeleteName = itemToDelete.name
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("The " + itemToDeleteName + " (food sub category) has been deleted")
        return redirect(url_for('catalog_latest_updates'))
    else:
        return render_template(
            'delete_subCategory.html', mainCategory_id=mainCategory_id, subCategory_id=subCategory_id, item=itemToDelete)
    

if __name__ == '__main__':
    app.secret_key = "IsSECRET_Amany"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)