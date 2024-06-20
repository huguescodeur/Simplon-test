CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id)
);

CREATE TABLE request_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER REFERENCES users(id),
    description TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_id INTEGER REFERENCES request_statuses(id),
    price DECIMAL(10, 2),
    budget_validated BOOLEAN DEFAULT FALSE,
    director_approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE request_history (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES requests(id),
    action VARCHAR(255) NOT NULL,
    performed_by INTEGER REFERENCES users(id),
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

INSERT INTO roles (name) VALUES ('Demandeur'), ('Controleur'), ('Comptable'), ('Directrice');
INSERT INTO request_statuses (name) VALUES ('Submitted'), ('Price Added'), ('Validated by Comptable'), ('Approved by Director'), ('Completed');
