INSERT INTO user
  (username, password, first_name, last_name, email, gender, description)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f',
    'first',
    'last',
    'test@gmail.com',
    'FEMALE',
    'good'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79',
    'first',
    'last',
    'other@gmail.com',
    'MALE',
    'good too');

INSERT INTO apartment
  (room_number, bathroom_number, zip, street_address, city, state, name, landlord_id)
VALUES
  (2, 2, 98107, 'HAHA', 'Seattle', 'WA', '11', 1),
  (2, 1, 98107, 'HAHA', 'Seattle', 'WA', 'apt2', 2),
  (2, 1, 98107, 'HAHA', 'Seattle', 'WA', 'apt3', 1);

INSERT INTO nest
  (apartment_id, status)
VALUES
  (1, 'APPROVED'),
  (1, 'PENDING'),
  (2, 'PENDING'),
  (1, 'PENDING'),
  (1, 'PENDING'),
  (1, 'PENDING'),
  (1, 'PENDING'),
  (3, 'PENDING');

INSERT INTO reservation
  (nest_id, tenant_id, accept_offer)
VALUES
  (1, 1, 0),
  (1, 2, 1),
  (2, 2, 0),
  (3, 1, 0),
  (2, 1, 0),
  (4, 1, 0),
  (5, 1, 0),
  (6, 1, 0),
  (8, 1, 0),
  (8, 1, 0);
