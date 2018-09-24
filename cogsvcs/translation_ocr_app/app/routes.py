from flask import render_template, redirect, url_for, flash, request, jsonify
from app import appvar, db
from .forms import LoginForm, RegistrationForm, TranslatePDFForm, TranslateFreeText, DictionaryAlternativesForm, TranslateOCRForm

from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from flask_login import current_user, login_user
from app.models import User, Employee
from flask_login import logout_user, login_required

from util import doc_cracking
from util import api_calls
from util import storage

import uuid
import os


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


@appvar.route('/translate/pdf', methods=['GET', 'POST'])
def translate_pdf():
    form = TranslatePDFForm()
    title = "Translate PDF Document"
    results = None
    original = None

    if request.method == "POST":
        if 'upload' not in request.files:
            flash("No file attached")
            return redirect(request.url)
        file = request.files['upload']

        if file.filename == "":
            flash("No file attached")
            return redirect(request.url)
        
        if file:
            fname, ext = os.path.splitext(file.filename)
            fname_rand = fname + str(uuid.uuid4()) + ext
            filename = secure_filename(fname_rand)

            pdf_local_path = os.path.join(appvar.config["UPLOAD_FOLDER"], filename)

            file.save(pdf_local_path)

            # Crack the document
            original = doc_cracking.crack_pdf(pdf_local_path)
            # Translate the document

            from_lang = request.form["from_lang"]
            # The "Guess" option is set to "xx" but the api expects a NoneType 
            # to come through to generate a detect language call
            if from_lang == "xx":
                from_lang = None
            to_lang = request.form["to_lang"]

            results = api_calls.translate_text(original, from_lang, to_lang)
    
    return render_template("translate_document.html",title=title, form=form, original=original,results = results)

@appvar.route('/translate/available', methods=['GET', 'POST'])
def translate_available():
    results = api_calls.list_languages()
    return render_template("list_languages.html",title="Languages", results=results)

@appvar.route('/translate/freetext', methods=['GET', 'POST'])
def translate_freetext():
    form = TranslateFreeText()
    title="Translate Free Text"
    results = None
    original = ""

    if request.method == "POST":
        if 'body' not in request.form:
            flash("No text to translate was provided.")
            return redirect(request.url)
        
        original = request.form["body"]
        results = api_calls.translate_text(original, from_lang = None, to_lang=request.form["to_lang"])

    return render_template("translate_docfree.html",title=title, form=form, original=original, results = results)


@appvar.route('/translate/freetext/alternative', methods=['GET', 'POST'])
def translate_alternative():
    form = DictionaryAlternativesForm()
    title = "Dictionary Lookup"
    original = None
    results = None
    error = None
    
    if request.method == "POST":
        if 'phrase' not in request.form:
            flash("No text to translate was provided.")
            print("Hit loop back")
            return redirect(request.url)
    
        original = request.form["phrase"]
        results = api_calls.translate_alternatives(original, request.form["from_lang"], request.form["to_lang"])

        if len(results) == 0:
            error = "No results, please refine your search."

    
    return render_template("dictionary_lookup.html",title=title, form=form, original=original, results = results, error = error)


@appvar.route('/translate/ocr', methods=['GET', 'POST'])
def translate_ocr():
    form = TranslateOCRForm()
    title = "Translate Image with OCR"
    results = None
    original = None

    if request.method == "POST":
        if 'upload' not in request.files:
            flash("No file attached")
            return redirect(request.url)
        file = request.files['upload']

        if file.filename == "":
            flash("No file attached")
            return redirect(request.url)
        
        if file:
            # Save the document to blob and get back the new file name
            secure_file_name = storage.save_image(request, "upload")
            # Generage Image URL with SAS token for viewing
            img_url = storage.generate_img_url(secure_file_name)
            # Pull out the text inside the image
            _ocr_from_lang = request.form["from_lang"] if request.form["from_lang"] != "xx" else "unk"
            ocr_results = api_calls.ocr_image(img_url = img_url, from_lang= _ocr_from_lang, mode=request.form["mode"] )

            # Define the "original" text
            original = ocr_results
            # Take text and translate

            from_lang = request.form["from_lang"]
            # The "Guess" option is set to "xx" but the api expects a NoneType 
            # to come through to generate a detect language call
            if from_lang == "xx":
                from_lang = None
            to_lang = request.form["to_lang"]

            results = api_calls.translate_text(original, from_lang, to_lang)
    
    return render_template("translate_ocr.html", title=title, form=form, original=original,results = results)