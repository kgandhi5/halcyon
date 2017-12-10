from flask import Flask, render_template, redirect, url_for, jsonify
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectMultipleField, RadioField
from wtforms.validators import Length, InputRequired
import json, os
import Final_Data

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'halcyon_danger'
Bootstrap(app)

# dump json to file for consumption by whatever else needs it
def retrieve_json_file(filename, resource_dir="res/geojson"):
    #if ( quiet != 1):
    #    print("# save to file")
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))

#    # make sure file is updated
#    run_model_hook(runhook)

    # open file as json
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)
    #debug# print("loaded %s" % filepath)

    # read into python structure - TODO: not best practice, return json string instead?
    # loadedroute = json.loads(loadedjson)

    # return json string
    return loadedjson

class FilterForm(FlaskForm):
	address = StringField('Address')
	radius = DecimalField('Radius')
	incident_type = SelectMultipleField('Incident Type', choices=[('animal','Animal'),('flood','Flooding'),('fire','Fire')])

@app.route('/', methods=('GET','POST'))
def index():
	form = FilterForm()
	if form.validate_on_submit():
		#os.makedirs('res/geojson')
		with open('res/geojson/geodata.json', 'w+') as outfile:
			json.dump(Final_Data.update_map(form), outfile)
	return render_template('index.html', form=form)

@app.route('/map')
def map():
	return render_template('map.html')

@app.route('/rest/get/filterdata', methods=('GET','POST'))
def filterdata():
        #test_json = {
        #		"name":{
        #			"flower":"red",
        #			"blue":3
        #			}
        #		}
        # halcyon coords from google maps are *backwards* : 30.266965, -97.745684
	# test_json= {"geometry": {"type": "Point", "coordinates": [-97.745684, 30.266965]}, "type": "Feature", "properties": {}}
        test_json = retrieve_json_file("geodata.json")

        # return with correct header
	return jsonify(test_json)

if __name__ == '__main__':
	app.run(debug=True)

