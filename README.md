NSE REST API

Overview
This project is a Django-based web application designed to manage National Stock Exchange (NSE) data. It provides functionalities to upload CSV files containing NSE index prices, view, filter, and manage the data through a RESTful API. Additionally, it offers an admin interface for easy data management.

Features
CSV Data Upload: Users can upload CSV files containing NSE index prices data through the provided API endpoint or the admin interface.
API Endpoints: The application provides RESTful API endpoints to retrieve, filter, and manage NSE index and price data.
Admin Interface: Built-in Django admin interface for easy management of data.
Data Filtering: Users can filter index prices data based on various parameters like open, high, low, close prices, shares traded, turnover, and date range.
Custom Management Command: Includes a custom Django management command to import data from a CSV file into the database.

Technologies Used
Django 5.0.2
Django REST Framework
PostgreSQL (as database backend)

API Endpoints
Indexes: /indexe/

GET: Retrieve a list of all indexes or create a new index.
POST: Create a new index.
Index Prices: /indexprices/

GET: Retrieve a list of all index prices or create a new index price.
POST: Create a new index price.
Index Data: /indexes/<int:pk>/

GET: Retrieve details of a specific index along with its prices data.
DELETE: Delete an index.
CSV Upload: /csvupload/

POST: Upload a CSV file containing index prices data.

Custom Management Command
To import data from a CSV file into the database, use the following command:

python manage.py importdata <file_path> <index_name>

<file_path>: Path to the CSV file.
<index_name>: Name of the index for which data is being imported (Choose from: 'NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY NEXT 50', 'NIFTY NEXT 50').