import os

from CRUD_Python_Module import (
    BaseAnimalShelter,
    CSVAnimalShelter,
    PostgresAnimalShelter,
    build_animal_shelter,
)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "dogs_dataset.csv")


def get_animal_shelter() -> BaseAnimalShelter:
    return build_animal_shelter(DATA_FILE)


def get_data_source_label(animal_shelter: BaseAnimalShelter) -> str:
    if isinstance(animal_shelter, PostgresAnimalShelter):
        return "PostgreSQL"
    if isinstance(animal_shelter, CSVAnimalShelter):
        return "CSV fallback"
    return "Unknown"
