from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

class ContactForm(FlaskForm):
    screenshot = FileField("Upload screenshot",validators=[FileRequired(),FileAllowed(['jpg','png','jpeg', 'Ensure you upload the right extension!'])])
    #fullname = StringField("Your name: ", validators=[DataRequired()]) #generate input of type text
    email = StringField("Your Email: ", validators=[Email(message="Hello, your email should be valid"),DataRequired()])
    message = TextAreaField("Message: ", validators=[DataRequired(),Length(min=10)])
    submit = SubmitField("Send Message: ")
    confirm_email = StringField("Confirm Email",validators=[EqualTo('email')])