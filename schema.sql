CREATE TABLE IF NOT EXISTS animals (
    animal_id VARCHAR(20) PRIMARY KEY,
    name TEXT,
    animal_type TEXT NOT NULL,
    breed TEXT NOT NULL,
    age_upon_outcome_in_weeks INTEGER,
    color TEXT,
    sex_upon_outcome TEXT,
    outcome_type TEXT,
    intake_type TEXT,
    intake_condition TEXT,
    location_lat DOUBLE PRECISION,
    location_long DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_animals_type_breed_age
    ON animals (animal_type, breed, age_upon_outcome_in_weeks);

CREATE INDEX IF NOT EXISTS idx_animals_breed
    ON animals (breed);

CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);

INSERT INTO users (username, password, question, answer)
VALUES ('admin', 'sha256$8fe4d475c33d370b3ef73f7017b70b4f630f7e70dbe757980f07eb61750a7795', 'Favorite color?', 'blue')
ON CONFLICT (username) DO NOTHING;
