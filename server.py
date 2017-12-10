from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectMultipleField, RadioField
from wtforms.validators import Length, InputRequired
import process_danger as Danger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'halcyon_danger'
Bootstrap(app)

class FilterForm(FlaskForm):
	address = StringField('Address')
	radius = DecimalField('Radius')
	incident_type = SelectMultipleField('Incident Type', choices=[('animal','Animal'),('flood','Flooding'),('fire','Fire')])

@app.route('/', methods=('GET','POST'))
def index():
	form = FilterForm()
	if form.validate_on_submit():
		Danger.processInputs(form)
	return render_template('index.html', form=form)

@app.route('/map')
def map():
	return render_template('map.html')

if __name__ == '__main__':
	app.run(debug=True)

