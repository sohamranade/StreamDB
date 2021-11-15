
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://ssr2182:1364@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)
  #print(request.form)


  #
  # example of a database query
  #
  #cursor = g.conn.execute("SELECT s.name, s.subscription_cost FROM streamingplatform WHERE s.name=name")
  #names = []
  #for result in cursor:
  #  names.append(result['name'])  # can also be accessed using result[0]
  #cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
# for Showing specific pages
@app.route('/stream_plat/<name>')
def stream_plat(name):
  cursor = g.conn.execute("SELECT e.name,e.genre, e.language,e.description FROM streamingplatform s, ison i,entertainment e WHERE s.name=%s AND s.name=i.name AND i.e_id=e.e_id",name)
  entertainment=[]
  for result in cursor:
    entertainment.append(result)
  cursor.close()
  context= dict(data=entertainment,stream=name)
  return render_template("stream_plat.html", **context)

@app.route('/movie/<name>')
def movie(name):
  return render_template("movie.html")

@app.route('/artist/<name>')
def artist(name):
  return render_template("artist.html")

@app.route('/tv_show/<name>')
def tv_show(name):
  cursor = g.conn.execute("SELECT DISTINCT e.name,e.genre, e.language,e.description, c.first_name,c.last_name,w_e.role FROM entertainment e, workedine w_e, castandcrew c WHERE e.name=%s AND e.e_id=w_e.e_id AND w_e.c_id=c.c_id",name)
  entertainment=[]
  for result in cursor:
    entertainment.append(result)
  cursor.close()
  context= dict(data=entertainment,stream=name)
  return render_template("tv_show.html",**context)

@app.route('/another')
def another():
  return render_template("another.html")


# Simple search bar
@app.route('/search', methods=['GET'])
def search():
  print(request.args)
  type_of= request.args['option']
  name= request.args['name']
  if type_of=='movie':
    return redirect(('movie/{}'.format(name)))
  elif type_of=='stream_plat':
    return redirect(('stream_plat/{}'.format(name)))
  elif type_of=='tv_show':
    return redirect(('tv_show/{}'.format(name)))
  elif type_of=='artist':
    return redirect(('artist/{}'.format(name)))
  #name = request.form['name']
  #g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  #return redirect('/')





#Everything related to logins and Signups.
@app.route('/signup',methods=["GET"])
def signup():
  return render_template("signup.html")

@app.route('/user_signup',methods=['POST'])
def user_signup():
  email=request.form['email']
  f_name=request.form['f_name']
  l_name=request.form['l_name']
  name= f_name+" "+ l_name
  dob=request.form['dob']
  password=request.form['psw']
  cursor= g.conn.execute("SELECT * FROM users u WHERE u.email_id=%s",email)
  row=cursor.fetchall()
  if not row:
    cursor1=g.conn.execute("SELECT MAX(u.u_id) FROM users u")
    res= cursor1.fetchall()
    u_id=res[0][0]
    u_id+=1
    #g.conn.execute('INSERT INTO users(u_id,email_id,name,dob,password) VALUES(%s,%s,%s,%s,%s)',(u_id,email,name,dob,password))
    print("Successfully inserted")
    cursor1.close()
  else:
    print(row)
    print("User Repeated")
  cursor.close()
  return redirect('/signup')
  
@app.route('/login',methods=["GET"])
def login():
  return render_template("login.html")

@app.route('/user_login',methods=["POST"])
def user_login():
  email=request.form['email']
  password=request.form['psw']
  cursor= g.conn.execute("SELECT u.u_id FROM users u WHERE u.email_id=%s and u.password=%s",(email,password))
  rows=cursor.fetchall()
  if not rows:
    print("Login Failed, Please check the login details")
    cursor.close()
    return render_template("login.html")
  else:
    u_id=rows[0][0]
    cursor.close()
    return redirect(('user/{}'.format(u_id)))

@app.route('/user/<u_id>')
def user(u_id):
  cursor= g.conn.execute("SELECT u.name FROM users u where u.u_id=%s",u_id)
  row=cursor.fetchall()
  name=row[0][0]
  context=dict(name=name)
  return render_template("user.html",**context)

@app.route('/rating_review',methods=["POST"])
def user_review():
  u_id= int(request.form['u_id'])
  name=request.form['name']
  rating=int(request.form['rating'])
  review= request.form['review']
  cursor= g.conn.execute("SELECT * from entertainment e where e.name=%s",name)
  rows=cursor.fetchall()
  cursor.close()
  if not rows:
    print(f"{name} doesnt exist in the database")
    return redirect("user/{}".format(u_id))
  else:
    e_id=rows[0][0]
    g.conn.execute("INSERT into review VALUES (%s,%s,%s,%s)",(u_id,e_id,rating,review))
    print("Sucessfully Inserted")
    return redirect("user/{}".format(u_id))






if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
