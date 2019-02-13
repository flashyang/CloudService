DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Nest;
DROP TABLE IF EXISTS Apartment;
DROP TABLE IF EXISTS User;

CREATE TABLE user (
user_id	INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL,
first_name TEXT,
last_name TEXT,
email TEXT,
gender TEXT CHECK( gender IN ('Male', 'Female', 'Unknown')),
description TEXT
);

CREATE TABLE apartment (
apartment_id INTEGER PRIMARY KEY AUTOINCREMENT,
room_number INTEGER NOT NULL,
bathroom_number INTEGER NOT NULL,
created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
street_address TEXT NOT NULL,
city TEXT NOT NULL,
state TEXT CHECK( state IN ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY')) NOT NULL, 
zip INTEGER NOT NULL,
price INTEGER NOT NULL,
sqft INTEGER NOT NULL,
name TEXT,
description TEXT,
landlord_id INTEGER NOT NULL,
photo_URL TEXT,
FOREIGN KEY (landlord_id) REFERENCES user (user_id)
);


CREATE TABLE nest (
nest_id INTEGER PRIMARY KEY AUTOINCREMENT,
apartment_id INTEGER NOT NULL,
status TEXT CHECK( status IN ('PENDING', 'APPROVED', 'REJECTED'))  NOT NULL DEFAULT 'PENDING', 
FOREIGN KEY (apartment_id) REFERENCES apartment (apartment_id)
);

CREATE TABLE reservation (
reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
nest_id INTEGER NOT NULL,
tenant_id INTEGER NOT NULL,
created TIMESTAMP NOT NULL, 
cancelled TINYINT(1) NOT NULL, 
FOREIGN KEY (nest_id) REFERENCES nest (nest_id),
FOREIGN KEY (tenant_id) REFERENCES user (user_id)
);


  	  

  


