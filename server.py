#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
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
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://aaa2325:0011@35.231.44.137/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

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
    print "uh oh, problem connecting to database"
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
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  

  cursor = g.conn.execute("SELECT S.name, S.employee_count, F.name, I.industry_name FROM Startups S JOIN Founder F ON F.startup_id = S.startup_id JOIN Primary_Industry I ON I.startup_id  = S.startup_id")
  names = []
  names.append(["Startup", "Employee Count", "Founder", "Industry",])
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
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

  context = dict(data = names)
 
  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/refresh')
def refresh():
  return redirect('/')


@app.route('/index')
def blah():
  return render_template("index.html")



@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/ind', methods=['POST'])
def indPage():


  ind = {"prod": 0 , "fin" : 0, "crowd" : 0, "real" : 0, "saas" : 0, 'music' : 0, 'tran': 0, 'analy': 0, 'mob' : 0, 'soc': 0, 'bus': 0, 'ele'  : 0, 'inte' : 0}
 

  trans = {"prod": "Productivity" , "fin" : "Fintech" , "crowd" : "Crowdfunding", "real" : "RealEstate", "saas" : "SAAS", 'music' : "Music" , 'tran': "Transportation", 'analy': "Analytics", 'mob' : "Mobile Devices", 'soc': "Social Media", 'bus': "Business Intelligence", 'ele' : "Electronics" ,  'inte' : "Internet"}
 
  query1 = "SELECT I.industry_name, COUNT(s.startup_id), I.average_valuation FROM Primary_Industry I LEFT OUTER JOIN Startups S ON S.startup_id = I.startup_id GROUP BY I.industry_name, I.average_valuation HAVING "


  for key in ind:
    temp = request.form.get(key)
    if(temp):
      ind[key] += 1

  count = 0

  for key in ind:
    if ind[key] == 1:
       if(count == 0):
         query1 += "I.industry_name = '" + trans[key] + "'"
       else:
	 query1 += " or I.industry_name = '" + trans[key] + "'"
       count += 1

  print(query1)

  cursor = g.conn.execute(query1)
  
  names = []
  names.append(["Industry", "Number of Startups", "Avg Valuation"]) 
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("another.html", **context)


	
@app.route('/acquirer', methods=['POST'])
def acquire():

  cursor = g.conn.execute("SELECT s.name, A.name, A.industry FROM Startups S JOIN Acquirer A on S.startup_id = A.startup_id")

  names = []
  names.append(["Startup", "Acquirer", "Acquirer Industry"]) 
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  
  return render_template("index.html", **context)




# Example of adding new data to the database
@app.route('/investinfo', methods=['POST'])
def investinfo():
  name = request.form['name']
  name = name + '%'
  print(name)
  cursor = g.conn.execute("SELECT S.name, I.investor_name, I.investment_amount, V.name, V.fund_size, A.name FROM Startups S JOIN Investor_Deal I ON I.startup_id = S.startup_id JOIN Venture_Capital_Fund V ON I.fund_id  = V.fund_id LEFT JOIN Acquirer A ON S.startup_id = A.startup_id  WHERE S.name LIKE %(name)s", {'name': name})
  names = []
  names.append(["Startup", "Investor Name", "Invest Amount", "VC Name", "VC Size", "Acquirer"]) 
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("index.html", **context)

@app.route('/industry', methods=['POST'])
def industry():
  name = request.form['name']
  name = name + '%'
  print(name)
  cursor = g.conn.execute("SELECT I.industry_name, COUNT(s.startup_id), I.average_valuation FROM Primary_Industry I LEFT OUTER JOIN Startups S ON S.startup_id = I.startup_id GROUP BY I.industry_name, I.average_valuation HAVING I.industry_name LIKE  %(name)s", {'name': name})

  names = []
  names.append(["Industry", "Number of Startups", "Avg Valuation"]) 
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("index.html", **context)

@app.route('/ginv', methods=['POST'])
def greaterInvest():
  name = request.form['name']
  print(name)
  if(name != ''):
    cursor = g.conn.execute("SELECT S.name, V.name, I.investor_name, I.investment_amount FROM Startups S JOIN Investor_Deal I ON I.startup_id = S.startup_id  JOIN Venture_Capital_Fund V ON V.fund_Id = I.fund_id WHERE I.investment_amount > %(name)s ORDER BY I.investment_amount", {'name': name})


  
    names = []
    names.append(["Startup", "VCF", "Investor", "Investment Amount"]) 
    for result in cursor:
      names.append(result)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = names)
  
  else:
    names = []
    context = dict(data = names)

  return render_template("index.html", **context)



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
