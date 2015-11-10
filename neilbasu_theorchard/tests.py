import unittest
import transaction

from sqlalchemy import create_engine
from pyramid import testing

from .models import (
    DBSession,
    Base,
    CuisineType,
    Restaurant,
    Inspection)
from .views import show_thai_restaurants
import os
from ConfigParser import SafeConfigParser

def setUpModule():
    path = os.path.dirname(os.path.realpath(__file__))
    ini_filepath = os.path.join(path, '..', 'development.ini')
    config_parser = SafeConfigParser()
    config_parser.read(ini_filepath)
    test_db_path = config_parser.get('app:main', 'testing.testdb')
    # create an engine bound to the test db
    engine = create_engine(test_db_path)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # create_all to create tables
    Base.metadata.create_all()

def tearDownModule():
    Base.metadata.drop_all()

class BaseTest(unittest.TestCase):
    def setUp(self):
        transaction.begin()

    def tearDown(self):
        transaction.abort()

    def _make_cuisine_type(self, name='foo(d)'):
        cuisine_type = CuisineType(name=name)
        DBSession.add(cuisine_type)
        return cuisine_type

    def _make_restaurant(self, cuisine_type, name='bar and grill'):
        restaurant = Restaurant(
            cuisine_type=cuisine_type,
            name=name,
            building='123A',
            street='Main Street',
            boro='Manhattan',
            zip_code='10001',
            phone_number='972-555-5555',
            camis=345
            )
        DBSession.add(restaurant)
        return restaurant

    def _make_inspection(self, restaurant, grade='A'):
        inspection = Inspection(
            restaurant=restaurant,
            critical_flag='foo',
            type='foo'
            )
        inspection.grade = grade
        DBSession.add(inspection)
        return inspection

class TestRestaurant(BaseTest):
    def test_address(self):
        # Address is generated from three other fields
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)
        DBSession.flush()
        self.assertEqual(
            restaurant.address,
            '123A Main Street, Manhattan 10001')

    def test_calculate_numeric_grade(self):
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)
        # let's make this restaurant 5-star
        self._make_inspection(restaurant=restaurant, grade='A')
        DBSession.flush()

        self.assertEqual(restaurant.calculate_numeric_grade(), 5)

        # One more good year
        self._make_inspection(restaurant=restaurant, grade='A')
        DBSession.flush()

        self.assertEqual(restaurant.calculate_numeric_grade(), 5)

        # Uh oh, they had a bad year
        # N/A should equal 2 in our setup
        self._make_inspection(restaurant=restaurant, grade='N/A')
        DBSession.flush()

        # Average of 5 + 5 + 2 == 4
        self.assertEqual(restaurant.calculate_numeric_grade(), 4)

    def test_grade(self):
        # Letter grades are based upon the database-stored numeric grades
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)

        # A
        restaurant.numeric_grade = 5
        DBSession.flush()

        self.assertEqual(restaurant.grade, 'A')

        # B
        restaurant.numeric_grade = 4
        DBSession.flush()

        self.assertEqual(restaurant.grade, 'B')

        # C
        restaurant.numeric_grade = 1
        DBSession.flush()

        self.assertEqual(restaurant.grade, 'C')

        # N/A
        restaurant.numeric_grade = 2
        DBSession.flush()

        self.assertEqual(restaurant.grade, 'N/A')

class TestInspection(BaseTest):
    def test_grade_hyrid_property_none_grade(self):
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)

        inspection = self._make_inspection(restaurant=restaurant, grade=None)
        self.assertIsNone(inspection._numeric_grade)
        self.assertIsNone(inspection.grade)

    def test_grade_hyrid_property_invalid_grade_not_applicable(self):
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)

        inspection = self._make_inspection(restaurant=restaurant, grade='Z')
        self.assertEqual(
            inspection._numeric_grade,
            Inspection.GRADE_TO_INT['N/A'])

    def test_grade_hyrid_property_normal_case(self):
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)

        inspection = self._make_inspection(restaurant=restaurant, grade='A')
        self.assertEqual(inspection._numeric_grade, 5)

        inspection.grade = 'B'
        self.assertEqual(inspection._numeric_grade, 4)

        inspection.grade = 'C'
        self.assertEqual(inspection._numeric_grade, 1)

        inspection.grade = 'N/A'
        self.assertEqual(inspection._numeric_grade, 2)

    def test_numeric_grade_property(self):
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)

        inspection = self._make_inspection(restaurant=restaurant, grade='A')
        self.assertEqual(inspection.numeric_grade, inspection._numeric_grade)

    def test_numeric_grade_sets_restaurant_grade(self):
        cuisine_type = self._make_cuisine_type()
        restaurant = self._make_restaurant(cuisine_type=cuisine_type)

        inspection = self._make_inspection(restaurant=restaurant, grade='A')
        self.assertEqual(restaurant.numeric_grade, inspection.numeric_grade)

class TestView(BaseTest):
    def test_show_thai_restaurants_ordered_by_ranking(self):
        thai_type = self._make_cuisine_type(name='Thai')
        restaurant1 = self._make_restaurant(
            cuisine_type=thai_type,
            name='mythai')
        restaurant1.numeric_grade = 2
        restaurant2 = self._make_restaurant(
            cuisine_type=thai_type,
            name='mythai')
        restaurant2.numeric_grade = 5

        DBSession.flush()

        dummy_request = testing.DummyRequest()
        response = show_thai_restaurants(dummy_request)
        # Sorted by ranking, best to worst
        self.assertListEqual(
            response['restaurants'],
            [restaurant2, restaurant1]
            )

    def test_show_thai_restaurants_returns_10(self):
        thai_type = self._make_cuisine_type(name='Thai')
        for i in range(20):
            restaurant = self._make_restaurant(cuisine_type=thai_type,
                name='rest%s' % str(i))
            restaurant.numeric_grade = 4

        DBSession.flush()

        dummy_request = testing.DummyRequest()
        response = show_thai_restaurants(dummy_request)
        self.assertEqual(
            len(response['restaurants']),
            10
            )

    def test_show_thai_restaurants_returns_request(self):
        dummy_request = testing.DummyRequest()
        response = show_thai_restaurants(dummy_request)
        self.assertEqual(
            response['request'],
            dummy_request
            )
