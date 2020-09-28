<!-- Heading -->
# LinkNYC Kiosk Real-Time Status

An ArcGIS script tool that retrieves data via API endpoint and gets json response from [NYC Open Data LinkNYC Kiosk Status](https://data.cityofnewyork.us/City-Government/LinkNYC-Kiosk-Status/n6c5-95xh) which gets updated hourly, writes geometries to a point feature class, and finally generates a pdf map showing each kiosk’s status on top of a base map. 

This tool is reusable. It can be used for the first time, as well as being used for updating data. Every time a user runs this tool, it will retrieve the latest data and create a new feature class and replace the old one in the geodatabase as long as the same output for the pdf map directory is chosen.