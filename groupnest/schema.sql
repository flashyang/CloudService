DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS nest;
DROP TABLE IF EXISTS apartment;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
user_id	INT PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(255) UNIQUE NOT NULL,
password VARCHAR(255) NOT NULL,
first_name VARCHAR(255),
last_name VARCHAR(255),
email VARCHAR(255),
gender ENUM ('MALE', 'FEMALE', 'OTHER'),
description VARCHAR(1024) DEFAULT ''
);

CREATE TABLE apartment (
apartment_id INT PRIMARY KEY AUTO_INCREMENT,
room_number INT NOT NULL,
bathroom_number INT NOT NULL,
created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
street_address VARCHAR(255) NOT NULL,
city VARCHAR(255) NOT NULL,
state ENUM('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY') NOT NULL, 
zip INT NOT NULL,
price INT NOT NULL DEFAULT 0,
sqft INT NOT NULL DEFAULT 0,
name VARCHAR(255),
description VARCHAR(1024) DEFAULT '',
landlord_id INT NOT NULL,
photo_URL VARCHAR(255) DEFAULT '',
FOREIGN KEY (landlord_id) REFERENCES user (user_id)
);


CREATE TABLE nest (
nest_id INT PRIMARY KEY AUTO_INCREMENT,
apartment_id INT NOT NULL,
status ENUM('PENDING', 'APPROVED', 'REJECTED')  NOT NULL DEFAULT 'PENDING', 
FOREIGN KEY (apartment_id) REFERENCES apartment (apartment_id)
);

CREATE TABLE reservation (
reservation_id INT PRIMARY KEY AUTO_INCREMENT,
nest_id INT NOT NULL,
tenant_id INT NOT NULL,
created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
accept_offer INT NOT NULL DEFAULT 0,
FOREIGN KEY (nest_id) REFERENCES nest (nest_id),
FOREIGN KEY (tenant_id) REFERENCES user (user_id)
);

  


