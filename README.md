Extract Monday Deals
By Tyler Schmalz (tylers@edmodo.com)

This program allows you to fill a Google sheet, based on information from Monday.com

Overview
--------

You run monday.py through the command-line:

python3 monday.py MondayCreds.yaml GoogleCreds.json

where:
  * MondayCreds.yaml is a simple yaml file containing your Monday.com API key.
  * GoogleCreds.json is a JSON file containing credentials for a google service account.

Setting up
----------
This program needs the following non-standard libraries:
  * gspread (pip install gspread)
  * pandas (pip install pandas)
  * yaml (pip install pyyaml)

Service Accounts
----------------
The program requires a Google service account.  Here is documentation on how
to set up a service account:

https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account

This service account also needs to have editor access to the Google Sheet where
you would like to store information from Monday.com.
