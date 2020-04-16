File Structure
	-Notebooks: contains three Jupyter Notebook, covering code from data cleaning to modeling.
	-Data: original and processed data for Notebooks
	-CSVFiles: text files for necessary data
	-JsonFiles: geojson files for map plotting
	-Models: prediction model, model parameter description
	-assets: css style files, website icon
	-app.py: main python file for website deployment
	-utils.py: utility functions for the application
	-Credentials: store credentials for Mapbox and Google Street View features
	
Installation and Execution
	-- Our application is hosted on heroku.com, website address is:
		https://test-denver.herokuapp.com/
	-- To host our website locally, a python version of or above 3.7.6 is needed
		a. download and unzip 'denver-housing' folder
		b. open the command line
		c. nagivate to 'denver-housing' folder
		d. run the following code
			> pip install numpy pandas dash dash_core_components dash_html_components dash_bootstrap_components dash_table xgboost jsonschema
			> python app.py
		e. open website with any internet browser using following address
			http://127.0.0.1:8050
		
		Notes: we use credentials to show additional features such as Google Street View picture for each house, to use such feature, please copy and paste your Mapbox access token to 'Credentials/mapbox_access_token.txt' file, and Google Street View Static API key to 'Credentials/google_street_view_api.txt'. Additional features should now work.
