# You.com Backend Takehome Challenge

We're going to be integrating with a JSON API that returns image URLs.
It's hosted [here](https://youdotcom-interview-api.azurewebsites.net/api/HttpAPI). 

The requirements are the following:
1. Build a web server hosted at a url of your choice, preferably using Python.
2. It should expose a few routes:
    - `GET /metadata/{image_index}` return the URL and title of the image with that index.
    - `GET /image/{image_index}` download the image from its URL and return it base64 encoded.
    - `GET /images` this should return all of the images base64 encoded.
    - `GET /images?filter=<PROP>` add a query parameter that allows you to filter by an image property to remove any duplicates. If the property doesn't exist, you should return the proper HTTP status code

Bonus points:
- Add caching so that you don't need to hit our API everytime

This is a timed exercise. Commit your work as soon as you are finished and make sure to include below the instructions on how to run the code and how to send requests to your API.


## Your instructions:
Description:
This application uses Python flask for Web server.
The application provides three end points /metadata/<int:image_index, /image/<int:image_index>, /images.

In an ideal scenario could leverage redis for caching image metadata. 
For simplicity used hashmap for caching the image metadata.
Alternatively used MySQL for storing and retrieving image metadata.(This is optional)
Actual images can be ported to filesystems like s3/azure. 
Used local images directory.
For an end to end design, when new images are uploaded would update the cache and local DB for less refreshes.
Also for scaling the application can introduce LRU caching to ensure high performance and low latency.


Steps to run the application:
1. Clone the Repository
   a. git clone https://github.com/Su-Sea/takehome-BackendEng-JayaDaggula.git
   b. cd takehome-BackendEng-JayaDaggula
2. Setup Virtual Environment
   a. python3 -m venv venv
   b. source venv/bin/activate
3. Install Dependencies
   a. pip install -r requirements.txt
4. This step only to route the application to run on MySQL (**Optional**)
   1. Connect to local MySQL DB
   2. Run command to create a new Database: `CREATE DATABASE youdotcom_takehome_db;`
   3. Create user: `create user 'youdotcom_takehome_db' identified by 'youdotcom_takehome_db'; Change the username and password as required
   4. Grant privileges: `GRANT ALL on youdotcom_takehome_db.* TO 'youdotcom_takehome_db' WITH GRANT OPTION;`
   5. Use database: `use youdotcom_takehome_db;`
   6. Create Table: `CREATE TABLE image_metadata (
       id INT AUTO_INCREMENT PRIMARY KEY, 
       image_index INT NOT NULL,
       title VARCHAR(255) NOT NULL, 
       url VARCHAR(255) NOT NULL, 
       file_path VARCHAR(255) NOT NULL, 
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       CONSTRAINT uq_index UNIQUE (image_index)
       );`
   7. Update connection details in repository/images.py with correct credentials. 
   8. Lastly Change `USE_DATABASE = True` in constants.py
5. Run the Application using `python app.py`
6. Test the endpoints by opening: 
   1. Get Metadata: http://127.0.0.1:5000/metadata/3
   2. Get image: http://127.0.0.1:5000/image/3
   3. Get images: http://127.0.0.1:5000/images
   4. Get images: http://127.0.0.1:5000/images?filter=title
   5. Get images: http://127.0.0.1:5000/images?filter=url
   6. Get images: http://127.0.0.1:5000/images?filter=invalid_metadata
Below are for Production release: 
7. To change the endpoint from local host to a named host change below code:
   ```
   if __name__ == "__main__":
       app.run(debug=True)
   ```
   to 
   ```
   if __name__ == "__main__":
       app.run(host="youdotcom_takehome_db.local", port=5000, debug=True)
   ```
   in app.py.
8. make an entry in `/etc/hosts` as `127.0.0.1 youdotcom_takehome_db.com.local`
9. Code Structure:
10. Project(takehome-BackendEng-JayaDaggula)/ 
    1.  | 
    2.  |--> app.py           # Main Flask app and visible endpoints 
    3.  |--> requirements.txt # Required python packages 
    4.  |--> README.md        # Initial Setup steps 
    5.  |--> handler/         # Entry to core logic. In case of any mapping needs these can be done in handler. 
    6.  |--> controller/      # Core Logic with validations, calling gateways other controllers, etc. 
    7.  |--> gateway/         # External service/api related code 
    8.  |--> images/          # Directory to store images(This can be replaced by S3/azure)
    9.  |--> constants.py     # All constants 
    10. |--> utils/           # common used utilities 
    11. |--> repository/      # Local DB related code. (MySQL) Can extend to SQLAlchemy or some ORM's

