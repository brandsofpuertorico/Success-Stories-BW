orgullopr
=========

# Starting out
1. Clone repository
2. If you don't have [MongDB](http://mongodb.org) installed you'll have to install it. `brew install mongo`
3. After installing make sure to run `mongod` in a terminal tab and keep it open running your local database.
4. `cd` into orgullopr directory.
5. Run `mongo orgullopr mongo_inserts.js`.
6. Create a virtual environment using [Virtualenv](http://www.virtualenv.org/en/latest/virtualenv.html) ```virtualenv venv```
7. Activate virtualenv source ```source venv/bin/activate```
8. Using pip install requirements from requirements.txt: ```pip install -r requirements.txt```
9. If no errors came up run the app with: ```python app.py``` and access the app through the ip and port the command returns.
10. To deactivate vitualenv source execute ```deactivate```
