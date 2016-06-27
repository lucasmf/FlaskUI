# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import json
import highlight

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
orderedClusters = []

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print ('Initialized the database.')

@app.route('/')
def show_entries():
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()

    with open('response.json') as data_file:
    	data = json.load(data_file)

    dict = {}

    for i in data:
    	dict[i['UsedFix']] = dict.get(i['UsedFix'], 0)

    global orderedClusters 

    beforeExample = data[0]['before']
    afterExample = data[0]['after']
    beforeExample2 = data[1]['before']
    afterExample2 = data[1]['after']

    beforeMap = {'example':beforeExample, 'example2':beforeExample2}
    afterMap = {'example':afterExample, 'example2':afterExample2}

    files = highlight.diff_files(beforeMap, afterMap, 'full')

    for line in files['example']:
        print(line.lala())

    for x in dict.keys():
        item = (x, dict.get(x))
        if(type(item[0]) == type(u'unicode')):
            orderedClusters.append((item[0].replace("\\", ""), item[1]))
        else:
            orderedClusters.append(item)

    orderedClusters = sorted(orderedClusters, key=lambda cluster: -cluster[1])

    return render_template('layout.html', clusters = orderedClusters, beforeExample = beforeExample, afterExample = afterExample, files = [[files['example']], [files['example2']]], selected = 0)\

# @app.route('/<int:cluster_id>')
# def show_post(post_id):
    

# def code(name, submit, bid):
#     assign = get_assignment(name)
#     backup = Backup.query.get(bid)
#     if not (backup and backup.submit == submit and
#             Backup.can(backup, current_user, "view")):
#         abort(404)
#     diff_type = 'full'
    
#     # highlight files and add comments
#     files = highlight.diff_files(assign.files, backup.files(), diff_type)
#     return render_template('student/assignment/code.html',
#         course=assign.course, assignment=assign, backup=backup,
#         files=files, diff_type=diff_type)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    # initdb_command()
    app.run()
