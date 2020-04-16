## Project Description
This repository hosts source code for our project on Denver housing market analytics. This project visualizes the analytics of Denver single family housing market, showing both historical and predicted house prices in Denver area. 

## File Structure

### |-- Notebooks
	This folder contains three Jupyter Notebook, covering code from data cleaning to modeling.
Initial data process was done in QGIS environment due to lack of common keys in different data sets. To link single family house records and neighborhood features, their spatial relationships were applied such that each property was assigned a neighborhood id to extract neighborhood-level attributes.

Also based on spatial relationship, we have summarized key features in each neighborhood, such as the number of crimes, traffic accidents, percentage of tree coverage. Distances to nearest food stores/schools/parks from each property were also calculated for model preparation.

### |-- Data
	This folder contains original and processed data for Notebooks
The key data is the historical house selling records associated with property details, collected from [Denver open data website](https://www.denvergov.org/opendata). The original data contains ~200,000 house sales records from 1945 to 2020. Of these, single family house records between 2000 and 2020 were filtered for inclusion in this project.

We also collected Denver neighborhood-level features from [Redfin](https://www.redfin.com/blog/data-center/) and [Denver website](https://www.denvergov.org/opendata), for the showing of demographical, socio-economic, environmental differences among neighborhoods.

The final data set is the consumer price index report, collected from [Bureau of Labor Statistics](https://data.bls.gov/cgi-bin/srgate), for inflation adjustment over the years.

### |-- CSVFiles
	text files for necessary data

### |-- JsonFiles
	geojson files for map plotting

### |-- Models
	house price prediction model, model parameter description

### |-- Credentials
	store credentials for Mapbox and Google Street View features

### |-- assets
	css style files, website icon

### |-- app.py
	main python file for website deployment
The intent is to provide users with comprehensive knowledge and extensive information related to their househunting in Denver by integrating historical transaction data, neighborhood characteristics and price predicting model.

The website was created with [Plotly Dash](https://plotly.com/) and hosted on [heroku](https://www.heroku.com/). It contains four tabs: 

	* Denver house: where web users see historical house sale records and  price prediction model.
	* Denver Neighborhood: where all neighborhood features and median sale prices can be queried, serving as a reference for house hunting.
	* Denver City: where we provide comparisons on key housing market metrics among cities that are similar to Denver.
	* About: where we provide a brief explanation of the entire project.

### |-- utils.py
	utility functions for the application
	
## Installation and Execution

Our application is hosted on [heroku](https://www.heroku.com/), website address is:
	https://test-denver.herokuapp.com/

To host our website locally, a python version of or above 3.7.6 is needed
	
	a. download and unzip 'denver-housing' folder
	b. open the command line
	c. nagivate to 'denver-housing' folder
	d. run the following code
		> pip install numpy pandas dash dash_core_components dash_html_components dash_bootstrap_components dash_table xgboost jsonschema
		> python app.py
	e. open website with any internet browser using following address
		http://127.0.0.1:8050
		
Notes: we use credentials to show additional features such as _Google Street View picture_ for each house, to use such feature, please copy and paste your Mapbox access token to 
	
	'Credentials/mapbox_access_token.txt', 
and Google Street View Static API key to 

	'Credentials/google_street_view_api.txt'. 
Additional features should now work.
