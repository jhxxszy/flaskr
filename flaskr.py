from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import *
from app import app, db, User, entries

DATABASE='flaskr.db'
DEBUG=True
SECRET_KEY='development key'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

db.create_all()

@app.route('/')
def show_entries():
    cur = db.session.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    new_entry = entries(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username_in = request.form["username"]
        password_in = request.form["password"]  
        r_password= User.query.filter_by(username=username_in).first()
        if r_password is None :
            error = 'Does not exsit'
        elif r_password.password != password_in :
            error = 'Password is wrong'
        else :
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['repeatpassword']
        if username == '' :
          error='Username can not be empty'
        elif password =='':
          error = 'Password can not be empty'
        elif User.query.filter_by(username=username).first() is None :
           if password != password2 :
                error = 'Password is not the same'
           else :
                new_admin = User(username, password)
                db.session.add(new_admin)
                db.session.commit()
                flash('Register successfully!')
                session['logged_in'] = True
                return redirect(url_for('show_entries'))
        else :
            error = 'The username already exists,try another one'
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()

