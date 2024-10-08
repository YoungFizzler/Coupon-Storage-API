This Flask application provides a simple API for user authentication and data management. It uses TinyDB to store user and entry data, and JWT for token-based authentication.

**Endpoints**

### Login Endpoint (`/login`)

* **Method**: `POST`
* **Description**: Authenticates a user with the provided username and password.
* **Request Body**:
	+ `username`: The username of the user to authenticate (required).
	+ `password`: The password of the user to authenticate (required).
* **Response**:
	+ `200 OK`: A JSON object containing a valid JWT token if authentication is successful.
	+ `400 Bad Request`: If the request body is missing required fields or contains invalid data.
	+ `401 Unauthorized`: If the username and password are incorrect or expired.
	+ `500 Internal Server Error`: If an internal error occurs during authentication.

### Signup Endpoint (`/signup`)

* **Method**: `POST`
* **Description**: Creates a new user with the provided username and password.
* **Request Body**:
	+ `username`: The username of the new user (required).
	+ `password`: The password of the new user (required).
* **Response**:
	+ `200 OK`: A JSON object containing a success message if the user is created successfully.
	+ `400 Bad Request`: If the request body is missing required fields or contains invalid data.
	+ `401 Unauthorized`: If the username already exists.
	+ `500 Internal Server Error`: If an internal error occurs during user creation.

### Add Entry Endpoint (`/add_entry`)

* **Method**: `POST`
* **Description**: Adds a new entry with the provided coupon barcode and username.
* **Request Body**:
	+ `username`: The username of the user who owns the entry (required).
	+ `coupon_barcode`: The coupon barcode of the entry (required).
* **Response**:
	+ `200 OK`: A JSON object containing a success message if the entry is added successfully.
	+ `400 Bad Request`: If the request body is missing required fields or contains invalid data.
	+ `500 Internal Server Error`: If an internal error occurs during entry creation.

### Remove Entry Endpoint (`/remove_entry`)

* **Method**: `POST`
* **Description**: Removes the entry with the provided coupon barcode and username.
* **Request Body**:
	+ `username`: The username of the user who owns the entry (required).
	+ `coupon_barcode`: The coupon barcode of the entry to remove (required).
* **Response**:
	+ `200 OK`: A JSON object containing a success message if the entry is removed successfully.
	+ `400 Bad Request`: If the request body is missing required fields or contains invalid data.
	+ `500 Internal Server Error`: If an internal error occurs during entry removal.

### View Entries Endpoint (`/view_entries`)

* **Method**: `GET`
* **Description**: Returns a list of all entries stored in TinyDB.
* **Request Body**: None
* **Response**:
	+ `200 OK`: A JSON object containing the list of entries if retrieval is successful.
	+ `500 Internal Server Error`: If an internal error occurs during entry retrieval.

### Token Verification

The `/login` endpoint generates a JWT token that can be used to authenticate subsequent requests. The `verify_token` function checks the validity and expiration of the provided
token in the `Authorization` header.

**Logging**

The application logs important events using a custom logging configuration with separate loggers for login, signup, add entry, remove entry, and view entries. Log messages are
written to log files for each type of event.

**Security Considerations**

* Always validate user input data to prevent SQL injection or other attacks.
* Use secure authentication mechanisms like JWT to protect sensitive information.
* Regularly update dependencies and libraries to ensure security patches are applied.
