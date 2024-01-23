from sqlalchemy import Integer, String, DateTime, Column, ForeignKey, TEXT, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import event
from psycopg2 import OperationalError #potrzebne do definicji silnika i laczenia z baza 
import sys
try:
    # Utworzenie silnika
    engine = create_engine("postgresql+psycopg2://your_username:your_password@your_host:your_port/your_database", echo=True)  # Użyj sqlite zamiast postgresql
    # Utworzenie sesji do interakcji z bazą danych
    Session = sessionmaker(bind=engine)
    session = Session()
except OperationalError as e:
    print(f"Błąd połączenia z bazą danych: {e}")
    exit()

# deklaracja bazy 
Base = declarative_base()

class AnimalSpecies(Base):
    __tablename__ = 'animal_species'
    id = Column(Integer, primary_key=True)
    species_name = Column(String)
    amount = Column(Integer)
    natural_environment = Column(String)
    habitat_id = Column(Integer, ForeignKey('habitat.id'))

    # Relacja z Animal
    animals = relationship("Animal", back_populates="species")

class Habitat(Base):
    __tablename__ = 'habitat'
    id = Column(Integer, primary_key=True)
    habitat_name = Column(String)
    surface = Column(Integer)

    animalspecies = relationship("AnimalSpecies", back_populates="habitat")

class Animal(Base):
    __tablename__ = 'animal'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species_id = Column(Integer, ForeignKey('animal_species.id'))
    sex = Column(String)
    birth_date = Column(Integer)

    # Relacja z AnimalSpecies
    species = relationship("AnimalSpecies", back_populates="animals")

# Dodaj tutaj inne definicje i konfigurację SQLAlchemy
    
Base.metadata.create_all(engine)

def dodaj_zwierze():
    session = Session()

    # Pobieranie danych od użytkownika
    imie = input("Podaj imię zwierzęcia: ")
    gatunek_id = input("Podaj ID gatunku: ")
    plec = input("Podaj płeć zwierzęcia: ")
    data_urodzenia = input("Podaj datę urodzenia zwierzęcia (w formacie RRRRMMDD): ")

    # Sprawdzenie, czy podano prawidłowe ID gatunku
    try:
        gatunek_id = int(gatunek_id)
    except ValueError:
        print("ID gatunku musi być liczbą.")
        return

    # Sprawdzenie, czy gatunek istnieje
    gatunek = session.query(AnimalSpecies).filter(AnimalSpecies.id == gatunek_id).first()
    if not gatunek:
        print("Gatunek o podanym ID nie istnieje.")
        return

    # Utworzenie nowego zwierzęcia
    nowe_zwierze = Animal(name=imie, species_id=gatunek_id, sex=plec, birth_date=data_urodzenia)
    session.add(nowe_zwierze)

    # Aktualizacja liczby występowania gatunku
    gatunek.amount = gatunek.amount + 1 if gatunek.amount else 1

    session.commit()
    print("Dodano nowe zwierzę do bazy.")



def czy_istnieje_zwierze_o_imieniu(imie):
    session = Session()
    istnieje = session.query(Animal).filter(Animal.name == imie).first() is not None
    session.close()
    return istnieje


def czy_istnieje_gatunek_o_nazwie(nazwa_gatunku):
    session = Session()
    istnieje = session.query(AnimalSpecies).filter(AnimalSpecies.species_name == nazwa_gatunku).first() is not None
    session.close()
    return istnieje


def finish():
    print("Finished.")
    session.close()
    sys.exit()


def wyswietl_zwierzeta():
    session = Session()
    zwierzeta = session.query(Animal).all()
    for zwierze in zwierzeta:
        print(f"ID: {zwierze.id}, Imię: {zwierze.name}, ID Gatunku: {zwierze.species_id}, Płeć: {zwierze.sex}, Data Urodzenia: {zwierze.birth_date}")
    session.close()

def wyswietl_gatunki():
    session = Session()
    gatunki = session.query(AnimalSpecies).all()
    for gatunek in gatunki:
        print(f"ID: {gatunek.id}, Nazwa Gatunku: {gatunek.species_name}, Ilość: {gatunek.amount}, Środowisko Naturalne: {gatunek.natural_environment}, ID Siedliska: {gatunek.habitat_id}")
    session.close()

def wyswietl_siedliska():
    session = Session()
    siedliska = session.query(Habitat).all()
    for siedlisko in siedliska:
        print(f"ID: {siedlisko.id}, Nazwa Siedliska: {siedlisko.habitat_name}, Powierzchnia: {siedlisko.surface}")
    session.close()

def edytuj_zwierze():
    session = Session()
    
    # Pobranie ID zwierzęcia od użytkownika
    zwierze_id = input("Podaj ID zwierzęcia do edycji: ")
    zwierze = session.query(Animal).get(zwierze_id)

    if zwierze:
        print(f"Edytujesz zwierzę: {zwierze.name}")

        # Umożliwienie użytkownikowi edycji różnych atrybutów
        nowe_imie = input("Nowe imię zwierzęcia (naciśnij enter, aby pozostawić obecne): ")
        nowy_species_id = input("Nowy ID gatunku (naciśnij enter, aby pozostawić obecny): ")
        nowa_plec = input("Nowa płeć zwierzęcia (naciśnij enter, aby pozostawić obecną): ")
        nowa_data_urodzenia = input("Nowa data urodzenia (naciśnij enter, aby pozostawić obecną): ")

        # Aktualizacja atrybutów (jeśli podano)
        if nowe_imie:
            zwierze.name = nowe_imie
        if nowy_species_id:
            zwierze.species_id = int(nowy_species_id)
        if nowa_plec:
            zwierze.sex = nowa_plec
        if nowa_data_urodzenia:
            zwierze.birth_date = int(nowa_data_urodzenia)

        session.commit()
        print("Zaktualizowano zwierzę.")
    else:
        print("Nie znaleziono zwierzęcia o podanym ID.")

    session.close()


def usun_zwierze():
    session = Session()
    
    zwierze_id = input("Podaj ID zwierzęcia do usunięcia: ")
    try:
        zwierze_id = int(zwierze_id)
        zwierze = session.query(Animal).get(zwierze_id)

        if zwierze:
            # Zmniejszenie liczby występowania gatunku
            gatunek = session.query(AnimalSpecies).filter(AnimalSpecies.id == zwierze.species_id).first()
            if gatunek and gatunek.amount > 0:
                gatunek.amount -= 1

            # Usunięcie zwierzęcia
            session.delete(zwierze)
            session.commit()
            print(f"Zwierzę o ID {zwierze_id} zostało usunięte.")
        else:
            print("Nie znaleziono zwierzęcia o podanym ID.")
    except ValueError:
        print("Podano nieprawidłowe ID. Proszę podać liczbę.")

    session.close()


def left_join_zwierzeta_gatunki():
    session = Session()
    # Wykonujemy left join tabel Animal oraz AnimalSpecies
    left_join_query = session.query(
        Animal.id, 
        Animal.name, 
        AnimalSpecies.species_name
    ).outerjoin(
        AnimalSpecies, 
        Animal.species_id == AnimalSpecies.id
    )

    # Iterujemy po wynikach złączenia, wyświetlając informacje
    for zwierze_id, zwierze_name, gatunek_name in left_join_query:
        print(f"ID Zwierzęcia: {zwierze_id}, Imię: {zwierze_name}, Gatunek: {gatunek_name or 'Nieznany'}")

    session.close()


def inner_join_gatunki_siedliska():
    session = Session()
    # Wykonujemy inner join tabel AnimalSpecies oraz Habitat
    inner_join_query = session.query(
        AnimalSpecies.species_name,
        Habitat.habitat_name,
        Habitat.surface
    ).join(
        Habitat,
        AnimalSpecies.habitat_id == Habitat.id
    )

    # Iterujemy po wynikach złączenia, wyświetlając informacje
    for species_name, habitat_name, surface in inner_join_query:
        print(f"Gatunek: {species_name}, Siedlisko: {habitat_name}, Powierzchnia: {surface}")

    session.close()


def wyswietl_menu():
    print("\n=== Menu Aplikacji Zoo ===")
    print("1. Dodaj zwierzę")
    print("2. Wyświetl wszystkie zwierzęta")
    print("3. Edytuj informacje o zwierzęciu")
    print("4. Usuń zwierzę")
    print("5. Sprawdź, czy istnieje zwierzę o danym imieniu")
    print("6. Wyświetl wszystkie gatunki")
    print("7. Sprawdź, czy istnieje gatunek o danej nazwie")
    print("8. Wyświetl wszystkie siedliska")
    print("9. Wyświetl zwierzęta z ich gatunkami (LEFT JOIN)")
    print("10. Wyświetl gatunki z ich siedliskami (INNER JOIN)")
    print("0. Zakończ")

def main():
    while True:
        wyswietl_menu()
        wybor = input("Wybierz opcję: ")

        if wybor == '1':
            dodaj_zwierze()
            
            # Tutaj dodajemy logikę do dodawania zwierzęcia
            # Zastąp 'pass' odpowiednim kodem
        elif wybor == '2':
            wyswietl_zwierzeta()
        elif wybor == '3':
            edytuj_zwierze()
        elif wybor == '4':
            usun_zwierze()
        elif wybor == '5':
            imie = input("Podaj imię zwierzęcia: ")
            istnieje = czy_istnieje_zwierze_o_imieniu(imie)
            print("Zwierzę istnieje." if istnieje else "Zwierzę nie istnieje.")
        elif wybor == '6':
            wyswietl_gatunki()
        elif wybor == '7':
            nazwa_gatunku = input("Podaj nazwę gatunku: ")
            istnieje = czy_istnieje_gatunek_o_nazwie(nazwa_gatunku)
            print("Gatunek istnieje." if istnieje else "Gatunek nie istnieje.")
        elif wybor == '8':
            wyswietl_siedliska()
        elif wybor == '9':
            left_join_zwierzeta_gatunki()
        elif wybor == '10':
            inner_join_gatunki_siedliska()
        elif wybor == '0':
            print("Zamykanie programu...")
            break
        else:
            print("Nieprawidłowy wybór. Proszę spróbować ponownie.")


main()





