import requests
import os,random,string, json
#import from 3rd party
from flask import render_template, request, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

#import from local files
from membapp import app,db,csrf
from membapp.models import Party, User, Topics, ContactUs, Comments, Lga, State,Donation,Payment
from membapp.forms import ContactForm

def generate_name():
    filename = random.sample(string.ascii_lowercase,10) #returns a list
    return ''.join(filename)

@app.route('/check_username',methods=['POST','GET'])
def check_username():
    if request.method == 'GET':
        return "Please complete the form normally"
    else:
        email = request.form.get('email')
        data = db.session.query(User).filter(User.user_email==email).first()
        if data == None:
            sendback = {'status':1,'feedback':"Email is available, please register"}
            return json.dumps(sendback)
        else:
            sendback = {'status':0,'feedback':"You already have an account. Click <a href='/login'>here</a> to login"}
            return json.dumps(sendback)


@app.route('/')
def home():
    #return app.config['SERVER_ADDRESS']
    contact = ContactForm()
    #connect to the endpoint to get the list of properties in JSON format,
    #convert to python dictionary and pass it to the template
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1.0/listall")
        if response:
            rspjson = json.loads(response.text)
        else:
            rspjson = dict()
    except:
        rspjson = dict() 
    return render_template("user/home.html",contact=contact,rspjson=rspjson) 

@app.route('/signup/')
def user_signup():
    p = db.session.query(Party).all()   #Party.query.all() 
    return render_template("user/signup.html",p=p)

#ASSIGNMENT
@app.route('/register/',methods=['POST'])
def register():
    #TO DO: retrieve all the form data and insert into User Table
    #set a session e.g. session['user'] = keep the email
    #redirect them to profile/dashboard
    if request.method == 'GET':
        return render_template('user/signup.html')
    else:
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        party = request.form.get('partyid')
        hashed_pwd = generate_password_hash(pwd)
        if email != "" and pwd != "" and party != "":
            u = User(user_fullname='',user_email=email,user_pwd=hashed_pwd,user_partyid=party)
            db.session.add(u)
            db.session.commit()
            #to get the id of the newly inserted record
            userid = u.user_id
            session['user'] = userid #keep the user id in session
            #flash("Registration Successful. login Here")
            return redirect(url_for('dashboard')) #create fxn dashboard
        else:
            flash("You must complete all the fields to signup")
            return redirect(url_for('user_signup'))

@app.route('/dashboard')
def dashboard():
    if session.get('user') != None:
        #retrieve the details of the logged in user
        id = session['user']
        deets = db.session.query(User).get(id)
        return render_template('user/dashboard.html',deets=deets)
    else:
        return redirect(url_for('user_login'))

# @app.route("/donate",methods=["POST","GET"])
# def donate():
#     if session.get('user') != None:
#         deets=User.query.get(session.get('user'))
#     else:
#         deets=None

#     if request.method == "GET":
#         return render_template('user/donation_form.html',deets=deets)
#     else:
#         #retrieve the form data and insert into Donation table
#         fullname = request.form.get('fullname')
#         amount = request.form.get('amount')
#         d = Donation(don_donor=fullname,don_amt=amount,don_userid=session.get('user'))
#         db.session.add(d)
#         db.session.commit()
#         session['donation_id'] = d.don_id
#         #generate the ref no and keep in session
#         refno = int(random.random()*10000000000)
#         session['reference'] = refno
#         return redirect("/confirm")
    
# @app.route("/confirm/",methods=["POST","GET"])
# @csrf.exempt
# def confirm():
#     if session.get('donation_id')!= None:
#         if request.method == "GET":
#             donor = db.session.query(Donation).get(session['donation_id'])
#             return render_template('user/confirm.html',donor=donor,refno=session['reference'])
#         else:
#             p = Payment(pay_donid=session.get('donation_id'),pay_ref=session['reference'])
#             db.session.add(p);db.session.commit()

#             don = Donation.query.get(session['donation_id'])  #details of the donation
#             donor_name = don.don_donor
#             amount = don.don_amt * 100
#             headers={"Content-Type":"application/json","Authorization":"Bearer sk_test_ebff11074bd6e6efff9fa005f23a0ec308da3aa5"}

#             data={"amount":amount,"reference":session['reference'],"email":donor_name}

#             response = requests.post("https://api.paystack.co/transaction/initialize",headers=headers,data=json.dumps(data))
#             rspjson = json.loads(response.text)
#             if rspjson['status']==True:
#                 url = rspjson['data']['authorization_url']
#                 return redirect(url)
#             else:
#                 return redirect('/confirm')
#     else:
#         return redirect('/donate')

# @app.route('/paystack')
# def paystack():
#     refid = session.get('reference')
#     if refid == None:
#         return redirect('/')
#     else:
#         #connect to paystack verify
#         headers={"Content-Type":"application/json","Authorization":"Bearer sk_test_ebff11074bd6e6efff9fa005f23a0ec308da3aa5"}
#         verifyurl = "https://api.paystack.co/transaction/verify/"+str(refid)
#         rspjson = json.loads(response.text)
#         if rspjson['status']== True:
#             #payment was successful
#             return rspjson
#         else:
#             #payment was not successful
#             return "payment was not successful"

@app.route('/login',methods=['POST','GET'])
def user_login():
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        #retrieve the form data
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        #query to check if username exists
        deets = db.session.query(User).filter(User.user_email==email).first()
        #compare pwd from from with hashed pwd in db
        if deets != None:
            pwd_indb = deets.user_pwd
            #compare with plain password from the form
            chk = check_password_hash(pwd_indb,pwd)
            if chk:
                id = deets.user_id
                session['user'] = id
                return redirect(url_for('dashboard'))
                #we should log the person in
            else:
                flash("Invalid password")
                return redirect(url_for('user_login'))
        else:
            flash("Invalid Username")
            return redirect(url_for('user_login'))

@app.route('/logout')
def user_logout():
    #pop the session and redirect to home page
    if session.get('user') != None:
        session.pop('user',None)
    return redirect('/')

@app.route('/load_lga/<stateid>',methods=['GET'])
def load_lga(stateid):
    #stateid = request.args.get('stateid')
    lgas = db.session.query(Lga).filter(Lga.lga_stateid==stateid).all()
    data2send = "<select class='form-control border-success'>"
    for s in lgas:
        data2send = data2send+"<option>" +s.lga_name+"</option>"
    data2send = data2send + "</select>"
    return data2send

@app.route('/profile',methods=['POST','GET'])
@csrf.exempt
def profile():
    id = session.get('user')
    if id == None: #means the user is not logged in
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            #deets = db.session.query(User).get(id)
            allstates = db.session.query(State).all()
            allparties = db.session.query(Party).all()
            deets = db.session.query(User).filter(User.user_id==id).first() 
            return render_template('user/profile.html',deets=deets,allstates=allstates,allparties=allparties)
        else:   #form was submitted
            fullname=request.form.get('fullname')
            phone=request.form.get('phone')
            #update the db using ORM method
            userobj = db.session.query(User).get(id)
            userobj.user_fullname = fullname
            userobj.user_phone = phone
            db.session.commit()
            flash("Profile Updated!")
            return redirect(url_for('profile'))

@app.route('/profile/picture/',methods=['POST','GET'])
def profile_picture():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == "GET":
            return render_template('user/profile_picture.html')
        else:
            #retrieve the file
            file = request.files['pix']
            #to know the original filename
            filename = file.filename
            filetype = file.mimetype

            allowed = ['.png','.jpg','.jpeg']

            if filename != '':
                name,ext = os.path.splitext(filename) #import os on line1
                if ext.lower() in allowed:
                    newname = generate_name()+ext
                    file.save('membapp/static/uploads/'+newname)
                    #update the user table using ORM
                    id = session['user']
                    userobj = db.session.query(User).get(id)
                    userobj.user_pix = newname
                    db.session.commit()
                    flash("Profile picture uploaded!")
                    return redirect(url_for('dashboard'))
                else:
                    return "File extension not allowed"
            else:
                flash('Please choose a file')
                return redirect (url_for('profile_picture'))
        
@app.route("/blog/")
def blog():
    articles = db.session.query(Topics).filter(Topics.topic_status=='1').all()
    return render_template('user/blog.html',articles=articles)

@app.route('/blog/<id>/')
def blog_details(id):
    # blog_deets = db.session.query(Topics).get(id)
    # blog_deets = Topics.query.get_or_404(id)
    blog_deets = db.session.query(Topics).filter(Topics.topic_id==id).first()
    if blog_deets:
        return render_template('user/blog_details.html',blog_deets=blog_deets)
    else:
        return redirect(url_for('blog') )

@app.route('/sendcomment')
def sendcomment():
    if session.get('user'):
        #retrieve the data coming from the request
        usermessage = request.args.get('message')
        #we can insert into db
        user = request.args.get('userid')
        topic = request.args.get('topicid')
        comment = Comments(comment_text=usermessage,comment_userid=user,comment_topicid=topic)
        db.session.add(comment)
        db.session.commit()
        commenter = comment.commentby.user_fullname
        dateposted = comment.comment_date
        sendback = f"{usermessage} <br><br>by {commenter} on {dateposted}"
        return sendback
    else:
        return "Comment was not posted, you need to be logged in"

@app.route("/newtopic",methods=["POST","GET"])
def newtopic():
    if session.get('user') !=None:
        if request.method == 'GET':
            return render_template('user/newtopic.html')
        else:
            #retrieve form data and validate
            content = request.form.get('content')
            if content != '':
                t = Topics(topic_title=content,topic_userid=session['user'])
                db.session.add(t)
                db.session.commit()
                if t.topic_id:
                    flash("Post successfully submitted for approval")
                else:
                    flash('Oops, something went wrong. Please try again')
            else:
                flash("You cannot submit an empty post")
            return redirect(url_for('blog'))
    else:
        return redirect(url_for('user_login'))

@app.route('/contact',methods=['GET','POST'])
@csrf.exempt
def contact_us():
    contact = ContactForm()
    if request.method == 'GET':
        return render_template('user/contact_us.html',contact=contact)
    else:
        if contact.validate_on_submit():
            #retrieve form data and insert into db
            upload = contact.screenshot.data #request.files.get('screenshot)
            email = request.form.get('email')
            msg = contact.message.data
            #insert into database
            m = ContactUs(msg_email=email,msg_content=msg)
            db.session.add(m)
            db.session.commit()
            flash("Thank you for contacting us")
            return redirect(url_for('contact_us'))
        else:
            return render_template('user/contact_us.html',contact=contact)

@app.route('/ajaxcontact',methods=['POST'])
def contact_ajax():
    email = request.form.get('email')
    msg = request.form.get('msg')
    return f"{email} says {msg}"


# @app.route('/demo')
# def demo():
#     #data = db.session.query(User.user_fullname,Party.party_name,Party.party_contact,Party.party_shortcode).join(Party).all()
#     #data = db.session.query(Party).filter(Party.party_id==1).first()
#     data = db.session.query(User).get(1)
#     return render_template('user/test.html',data=data)




#     data = db.session.query(User).filter(User.user_id==1).all() #returns a list
#     data = db.session.query(User).filter(User.user_id==1).first() #returns one result
#     data = db.session.query(User).get(1) #returns one result

#     data = User.query.filter(User.user_email==email, User.user_pwd==pwd).first()
#     data = User.query.filter(User.user_email==email, User.user_pwd==pwd).count() fetches the count
#     return render_template('user/test.html',data=data)