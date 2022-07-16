from flask import redirect, render_template
from flask_cors import cross_origin
from cuntapi.mladen_api import *

app = Flask(__name__)

with open('jsondata/all_data.json', 'r') as all_data:
    allData = json.load(all_data)
with open("jsondata/all_endpoints.json", 'r') as all_endppoints:
    endPoints = json.load(all_endppoints)
with open('jsondata/all_cities.json', 'r') as all_cities:
    allCities = json.load(all_cities)

continentsList = list(set([x["ContinentName"] for x in allData]))
countriesList = list(set([x["CountryName"] for x in allData]))


def iterAndConvert(keyword, iterList):
    return [{keyword: y} for y in iterList]


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(404)
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def page_not_found(e):
    return jsonify({"404": "Endpoint not found!"})


@app.route("/")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def index_page():
    return jsonify(endPoints)


@app.route("/v1/docs")
def docs_page():
    return render_template('docs.html')


@app.route("/v1/errors")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def error_page():
    error = request.args.get('error')
    allErrors = {"pecntr": {"Error": ["Please enter a country!", "Example: /v1/cities?country_name=Bulgaria"]},
                 "iecntr": {"Error": ["Country not found!", "Example: /v1/cities?country_name=Bulgaria"]},
                 "pecnt": {"Error": ["Please enter a continent!", "Example: /v1/countries?continent_name=Europe"]},
                 "iecnt": {"Error": ["Continent not found!", "Example: /v1/countries?continent_name=Europe"]}}
    return jsonify(allErrors.get(error, {"Hmm...": "If you're seeing this, either an error was not properly handled "
                                                   "or you manually came here"}))


@app.route("/v1/all_countries")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def all_countries():
    return jsonify(iterAndConvert("countryName", countriesList))


@app.route("/v1/continents")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def all_continents():
    return jsonify(iterAndConvert("continentName", continentsList))


@app.route("/v1/continents/<ctn>")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def country_by_continent(ctn):
    getCountries = list(
        set([x["CountryName"] for x in allData if x['ContinentName'] == ctn.title()]))
    return jsonify(iterAndConvert("countryName", getCountries))


@app.route("/v1/continents/<ctn>/<cntr>")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def city_by_country(ctn, cntr):
    return jsonify([{"cityName": y} for y in [x['cities'] for x in allCities if x.get('country') == cntr.title()][0]])


@app.route("/v1/countries")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def country_by_continents():
    try:
        ctn = request.args.get('continent_name')
        if not ctn:
            raise TypeError()
        else:
            getCountries = list(
                set([x["CountryName"] for x in allData if x['ContinentName'] == ctn.title()]))
            if len(getCountries) < 1:
                raise IndexError()
            else:
                return jsonify(iterAndConvert("countryName", getCountries))
    except TypeError:
        return redirect("/v1/errors?error=pecnt")
    except IndexError:
        return redirect("/v1/errors?error=iecnt")


@app.route("/v1/cities")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def cities_by_country():
    try:
        cntr = request.args.get('country_name')
        if not cntr:
            raise TypeError()
        else:
            return jsonify(
                [{"cityName": y} for y in [x['cities'] for x in allCities if x.get('country') == cntr.title()][0]])
    except TypeError:
        return redirect("/v1/errors?error=pecntr")
    except IndexError:
        return redirect("/v1/errors?error=iecntr")


if __name__ == "__main__":
    app.run(debug=True)
