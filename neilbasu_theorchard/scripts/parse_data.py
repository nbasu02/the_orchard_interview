from neilbasu_theorchard import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ConfigParser import SafeConfigParser
from dateutil.parser import parse as date_parse
import os
import sys
import transaction
import csv

# Columns on spreadsheet
NAME = 'DBA'
BUILDING = 'BUILDING'
STREET = 'STREET'
ZIP = 'ZIPCODE'
PHONE = 'PHONE'
BORO = 'BORO'
CUISINE_TYPE = 'CUISINE DESCRIPTION'
VIOLATION_CODE = 'VIOLATION CODE'
GRADE_DATE = 'GRADE DATE'
GRADE = 'GRADE'
FLAG = 'CRITICAL FLAG'
INSPECTION_TYPE = 'INSPECTION TYPE'
CAMIS = 'CAMIS'

def _get_or_create_cuisine_type(session, name):
    cuisine_type = session.query(models.CuisineType).filter(
        models.CuisineType.name==name
        ).first()

    if not cuisine_type:
        cuisine_type = models.CuisineType(name=name)
        session.add(cuisine_type)

    return cuisine_type

def _get_or_create_restaurant(session,
    name,
    camis,
    building,
    street,
    zip_code,
    boro,
    cuisine_type):

    restaurant = session.query(models.Restaurant).filter(
        models.Restaurant.name==name,
        models.Restaurant.camis==camis
        ).first()

    if not restaurant:
        restaurant = models.Restaurant(
            name=name,
            camis=camis,
            building=building,
            street=street,
            boro=boro,
            zip_code=zip_code,
            cuisine_type=cuisine_type
            )
        session.add(restaurant)

    return restaurant

def _create_inspection(session,
    grade,
    grade_date,
    violation_code,
    critical_flag,
    inspection_type,
    restaurant):

    inspection = models.Inspection(
        grade_date=grade_date,
        violation_code=violation_code,
        critical_flag=critical_flag,
        type=inspection_type,
        restaurant=restaurant
        )
    inspection.grade = grade

    session.add(inspection)
    return inspection

def main(session):
    path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(path,
        'DOHMH_New_York_City_Restaurant_Inspection_Results.csv')
    with open(filename) as restaurant_datafile:
        reader = csv.DictReader(restaurant_datafile)
        for row in reader:
            cuisine_type_name = row[CUISINE_TYPE]
            cuisine_type = _get_or_create_cuisine_type(
                session=session,
                name=cuisine_type_name
                )

            restaurant_name = row[NAME].strip()
            camis = row[CAMIS].strip()
            building = row[BUILDING].strip()
            street = row[STREET].strip()
            boro = row[BORO].strip()
            zip_code = row[ZIP].strip()

            restaurant = _get_or_create_restaurant(
                session=session,
                name=restaurant_name,
                camis=camis,
                building=building,
                street=street,
                boro=boro,
                zip_code=zip_code,
                cuisine_type=cuisine_type
                )

            grade = row[GRADE]
            grade_date = row[GRADE_DATE]
            violation_code = row[VIOLATION_CODE]
            critical_flag = row[FLAG]
            inspection_type = row[INSPECTION_TYPE]

            _create_inspection(
                session=session,
                grade=grade,
                grade_date=date_parse(grade_date),
                violation_code=violation_code,
                critical_flag=critical_flag,
                inspection_type=inspection_type,
                restaurant=restaurant
                )

            session.commit()
            sys.stdout.write('.')
            sys.stdout.flush()

if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    config_parser = SafeConfigParser()

    ini_filepath = os.path.join(path, '..', '..', 'development.ini')
    config_parser.read(ini_filepath)

    db_uri = config_parser.get('app:main', 'sqlalchemy.url')

    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    main(session)
