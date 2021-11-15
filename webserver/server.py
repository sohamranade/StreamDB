
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

@app.route('/best_platform')
def best_platform():


  #add toggle for all results/top result and for bang for buck/absolute number
  #category = "artist" #can be artist, genre, language, rating (threshold 4)
  #name = "Tom Cruise"
  name = request.args['name']
  category = request.args['category']
  
  T= ""

  if category=="artist":
    fname, lname = name.split()

    T = "Select distinct e_id from workedinM W, CastAndCrew C where W.c_id = C.c_id and C.first_name = '" 
    T += fname + "' and C.last_name = '" + lname + "' "  
  
  elif category == "genre":
    genre = name
    T = "Select distinct e_id from Entertainment Where genre = '" + genre + "' "
  
  elif category == "language":
    language = name
    T = "Select distinct e_id from Entertainment Where language = '" + language + "' "

  command = "Select name, count(e_id) From IsOn Where e_id in (" + T + ") "
  command+= "Group by name "
  command+= "order by count(e_id) desc"
  cursor = g.conn.execute(command)

  for result in cursor:
    print(list(result))
  
  cursor.close()

  return render_template("movie_search.html")  


@app.route('/movie_search')
def movie_search():
  
  name = request.args['name']
  artist = request.args['artist']
  language = request.args['language']
  platform = request.args['platform']
  genre = request.args['genre']
  sort_by_rating = "asc" #can be asc, desc, none ("")

  command = "Select E.e_id, name, rating, genre, language, release_year, running_time" 
  command+= " From Movies M, Entertainment E "

  where_part = "Where M.e_id = E.e_id"

  if(len(name) >0):
    where_part += " and E.name = '" + name + "'"
  
  if(len(language) >0):
    where_part += " and E.language = '" + language + "'"
  
  if(len(genre) >0):
    where_part += " and E.genre = '" + genre + "'"

  comm2 = ""
  comm3 = ""

  if len(artist)>0:
    fname, lname = artist.split()   #handle error where not 2 values to unpack
    comm2 = "Select e_id From WorkedInM W, CastAndCrew C Where W.c_id = C.c_id and C.first_name = '" 
    comm2 += fname + "' and C.last_name = '" + lname + "'"

  if len(platform)>0:
    comm3 = "Select e_id from IsOn Where name = '" + platform + "'"

  if len(comm2) > 0:
    where_part += " and M.e_id in (" + comm2 + ") "
  
  if len(comm3) > 0:
    where_part += " and M.e_id in (" + comm3 + ") "

  command += where_part

  if sort_by_rating == 'asc':
    command += " order by Rating ASC"
  
  if sort_by_rating == 'desc':
    command += " order by Rating DESC"
    
  cursor = g.conn.execute(command)
  
  for result in cursor:
    print(list(result))
  
  cursor.close()
  return render_template("movie_search.html")

@app.route('/movie/<name>')
def movie(name):
  
  cursor = g.conn.execute("Select e_id from Entertainment where name = '" + name + "'")
  rows = []
  for result in cursor:
    rows.append(list(result))  # can also be accessed using result[0]
  cursor.close()

  e_id = rows[0][0]
  
  command = "Select E.e_id, E.name, rating, genre, language, description, release_year, running_time" 
  command+= " From Movies M, Entertainment E "
  command+= "Where M.e_id = E.e_id and M.e_id = " + str(e_id)

  cursor = g.conn.execute(command)
  rows = []
  for result in cursor:
    rows.append(list(result))

  cursor.close()
  #print("#########################################")
  command = "Select C.first_name, C.last_name, W.role From WorkedInM W, CastAndCrew C Where W.c_id = C.c_id and W.e_id = "
  command += str(e_id)

  cursor = g.conn.execute(command)
  rows1 = []
  for result in cursor:
    rows1.append(list(result))
  cursor.close()

  context=dict(stream=name,data=rows, artist_data=rows1)
  return render_template("movie.html", **context)


@app.route('/artist/<name>')
def artist(name):

  f_name, l_name = name.split(' ')
  command = "Select c_id from CastAndCrew Where first_name = '" + f_name + "' and last_name = '" + l_name + "'"
  cursor = g.conn.execute(command)
  rows = []
  for result in cursor:
    rows.append(list(result))  # can also be accessed using result[0]
  cursor.close()

  c_id = rows[0][0]
  
  command = "Select W.role, E.name From WorkedInM W, Entertainment E Where W.e_id = E.e_id and W.c_id = " + str(c_id) 
  
  cursor = g.conn.execute(command)
  rows1 = []
  for result in cursor:
    rows1.append(list(result))

  cursor.close()

  command = "Select DISTINCT W.role, E.name From WorkedInE W, Entertainment E Where W.e_id = E.e_id and W.c_id = " + str(c_id) 
  
  cursor = g.conn.execute(command)
  for result in cursor:
    rows1.append(list(result))

  cursor.close()
  #print("#########################################")
  context=dict(stream=name, artist_data=rows, data=rows1)
  return render_template("artist.html", **context)

@app.route('/tv_show/<name>')
def tv_show(name):
  cursor = g.conn.execute("SELECT DISTINCT e.name,e.genre, e.language,e.description, c.first_name,c.last_name,w_e.role FROM entertainment e, workedine w_e, castandcrew c WHERE e.name=%s AND e.e_id=w_e.e_id AND w_e.c_id=c.c_id",name)
  entertainment=[]
  for result in cursor:
    entertainment.append(result)
  cursor.close()
  context= dict(data=entertainment,stream=name)
  return render_template("tv_show.html",**context)


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
    cursor= g.conn.execute("SELECT * from review r WHERE r.u_id=%s and r.e_id=%s",(u_id,e_id))
    rows1=cursor.fetchall()
    cursor.close()
    if not rows1:
      g.conn.execute("INSERT into review VALUES (%s,%s,%s,%s)",(u_id,e_id,rating,review))
      print("Sucessfully Inserted")
      '''
      cursor=g.conn.execute("SELECT e.rating,e.no_ratings FROM entertainment e WHERE e.e_id=%s",(e_id))
      res=cursor.fetchall()
      cursor.close()
      rate,n_rate=res[0]
      rate= ((rate*n_rate) + rating)/(n_rate+1)
      n_rate+=1
      g.conn.execute("UPDATE entertainment SET rating=%s, no_ratings=%s WHERE e_id=%s ",(rate,n_rate,e_id))
      '''
    else:
      cursor=g.conn.execute("SELECT e.rating,e.no_ratings, r.rating FROM entertainment e,review r WHERE e.e_id=%s,r.e_id=e.e_id and r.u_id=%s",(e_id,u_id))
      rows=cursor.fetchall()
      cursor.close()
      rate, n_rate, u_rate= rows[0]
      rate= (rate*n_rate - u_rate + rating)/n_rate
      g.conn.execute("UPDATE entertainment SET rating=%s, no_ratings=%s WHERE e_id=%s ",(rate,n_rate,e_id))
      print("Successfully updated")
      g.conn.execute("UPDATE review SET rating=%s, review=%s WHERE e_id=%s AND u_id=%s",(rating,review,e_id,u_id))
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
