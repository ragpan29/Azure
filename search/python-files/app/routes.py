from flask import render_template, redirect, url_for, flash, request, jsonify
from app import appvar, db
from .forms import LoginForm, RegistrationForm, SearchForm

from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from flask_login import current_user, login_user
from app.models import User, Employee
from flask_login import logout_user, login_required

from util import doc_cracking
from util import storage
from util import search
from util import graph as jsgraph

import uuid
import os
from urllib.parse import quote_plus, quote
import requests


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
    form = SearchForm()
    return render_template('index.html', title='Home', form=form)


@appvar.route('/search', methods=['GET','POST'])
def search_page():
    form = SearchForm()
    query = None
    results = []

    if form.validate_on_submit():
        sas_token = appvar.config["BLOB_SAS"]
        query = form.search.data
        query_string = {'search':quote_plus(query.strip()), "highlight":"content"}
        results = search.query_index(query_string)

        # Create Image URL 
        for doc in results:
            if doc["docType"] == "Handwritten":
                url = appvar.config["BLOB_URL"]+appvar.config["BLOB_CONTAINER"]+"/"+doc["parentDoc"]+sas_token
                doc.update({"img_url":url})
            

    return render_template('search.html', title="Search a Topic", form=form, results = results, query = query)

@appvar.route('/graph/<query>', methods=["POST","GET"])
def graph(query):
    form = SearchForm()
    results = []

    query_string = {'search':quote_plus(query.strip()), "$select":"entities"}
    results = search.query_index(query_string)

    list_of_entities_lists = [doc["entities"] for doc in results]

    nodes, edges = jsgraph.node_edge_creation(list_of_entities_lists, query)

    graph_dict = [{"id":i, "label":value} for i, value in nodes]

    return render_template('graph.html', 
        title='Relationship Mapping', 
        form = form ,
        query = query, 
        graph_dict= graph_dict,
        edge_list = edges,
        results = results
    )

