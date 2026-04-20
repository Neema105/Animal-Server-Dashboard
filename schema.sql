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
