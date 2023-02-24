from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

#we want to make the object-baseed config available
from membapp import config

app = Flask(__name__,instance_relative_config=True)

#initialize extension to protect all POST routes against csrf attack and pass the token when submitting through these routes
csrf = CSRFProtect(app)
csrf.exempt 

#load the config from instance folder file
app.config.from_pyfile('config.py',silent=False)
#load the config from object-based config that is within your package
app.config.from_object(config.LiveConfig)

db=SQLAlchemy(app)

#load the routes and form
from membapp import adminroutes,userroutes,paystack_routes