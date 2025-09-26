# GABCPL---Deflection-Check-App
GABCPL is a Streamlit web application designed to help civil and structural engineers check the deflection of ETABS projects. The app automates the process of reading an ETABS XML output file, calculating deflection limits based on industry standards, and presenting a clear, color-coded report.


This tool significantly reduces manual work by instantly identifying whether a structure's deflection is within acceptable limits.

Features
XML File Upload: Easily upload an ETABS XML output file directly from your machine.

Automated Deflection Check: The app automatically parses the XML data to find maximum deflections for specified load patterns (SPX, SPY, WX, WY, GX, GY).

Limit Calculation: Calculates deflection limits using the following formulas:

H / 250 for SPX, SPY, GX, and GY

H / 500 for WX and WY

H is the maximum story height from the XML file.

Color-Coded Status: The results table is color-coded for quick visual inspection. Green indicates that the deflection is within the limit, while red indicates it has been exceeded.

Excel Export: Download the complete report as an Excel (.xlsx) file for easy record-keeping and sharing.

Installation
To run this application, you need to have Python and Streamlit installed.

Clone this repository to your local machine:

git clone [your-repository-url]
cd gabcpl-app

Install the required Python packages using pip:

pip install -r requirements.txt

How to Run the App
Once the dependencies are installed, run the app from your terminal:

streamlit run app.py

The app will automatically open in your default web browser.

Usage
Click the "Browse files" button to upload your ETABS XML output file.

The app will process the file and display the deflection report in a table.

Review the table to see the Actual Deflection, Deflection Limit, and Status for each load pattern.

Click the "Download Data as Excel File" button to save the report to your machine.
