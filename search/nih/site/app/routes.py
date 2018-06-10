from flask import render_template, redirect, url_for, flash, request
from app import appvar, db
from .forms import SearchForm, LoginForm, RegistrationForm

from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user, login_required
import requests
from urllib.parse import quote_plus, quote

import sys

@appvar.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page) != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@appvar.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@appvar.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@appvar.route('/')
@appvar.route('/index')
def index():
    return render_template('index.html', title='Home')

@appvar.route('/secret')
@login_required
def hidden_page():
    return render_template('secret.html', title="Super Secret", 
    user=current_user)

def query_index(indexname, params):
    URL = appvar.config["SEARCH_URL"]
    API = '2017-11-11'
    KEY = appvar.config["QUERY_KEY"]
    headers = {'content-type': 'application/json', 'api-key': KEY}
    search_url = ''.join([URL, '/indexes/',indexname,'/docs?api-version=',API])

    search_results = requests.get(search_url, params=params, headers=headers)

    output={}
    if search_results.status_code == 200:
        output = search_results.json()

    return output

def query_key_phrase(text):
    URL = appvar.config["KEY_PHRASE_ULR"]
    KEY = appvar.config["KEY_PHRASE_KEY"]
    headers= {'Ocp-Apim-Subscription-Key': KEY}
    documents = {"documents": [{"id":1,"language":"en", "text":text}]}

    response  = requests.post(URL, headers=headers, json=documents)

    output = {}
    if response.status_code == 200:
        output = response.json()["documents"][0]["keyPhrases"]
    
    return output



@appvar.route('/search', methods=['GET','POST'])
def search():
    form = SearchForm()
    search_name = "Search"
    if form.validate_on_submit():
        query = form.search.data
        query_string = {'search':quote_plus(query.strip())}
        nih = query_index("nih-data", query_string)["value"]
        prod = query_index("product-data", query_string)["value"]

        return render_template('search.html', 
            title="Search Results - Prod:{} NIH:{}".format(len(prod),len(nih)),
            form=form, nih = nih, prod=prod, query = query, submitted = True, search_name = search_name)
    else:
        return render_template('search.html', title="Search a Topic", form=form, search_name = search_name)

@appvar.route('/searchprofile', methods=['GET','POST'])
def searchprofile():
    form = SearchForm()
    search_name = "Searching With a Profile"
    if form.validate_on_submit():
        query = form.search.data
        query_string = {'search':quote_plus(query.strip())}
        query_string2 = {'search':quote_plus(query.strip()),"scoringProfile":"weightedTitleTerms"}
        nih = query_index("nih-data", query_string2)["value"]
        prod = query_index("product-data", query_string)["value"]

        return render_template('search.html', 
            title="Search Results - Prod:{} NIH:{}".format(len(prod),len(nih)),
            form=form, nih = nih, prod=prod, query = query, submitted = True, search_name = search_name)
    else:
        return render_template('search.html', title="Search a Topic", form=form, search_name = search_name)


@appvar.route('/grant/<grant_key>')
def grant_detail(grant_key):
    query_string = {'key':quote_plus(grant_key)}
    grant = query_index("nih-data", query_string)
    key_terms = None
    related_prods = None

    if "abstract" in grant:
        terms = query_key_phrase(grant["abstract"])
        key_terms = ' or '.join(terms)
        print(key_terms, file=sys.stderr)
        abstract_query = {'search': quote(key_terms)}
        related_prods = query_index("product-data", abstract_query)["value"]

        print(related_prods, file=sys.stderr)

    if "projectnumber" not in grant:
        grant = None    

    return render_template('grant_detail.html', 
        title="Grant Details", grant=grant, related_prods = related_prods, key_terms = key_terms)
    