from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    ForeignKey,
    Date,
    event
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
    )
from sqlalchemy.ext.hybrid import hybrid_property
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class Base(object):
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)

class Restaurant(Base):
    __tablename__ = 'restaurant'

    name = Column(Text)
    cuisine_type_id = Column(ForeignKey('cuisine_type.id'))

    # External id for restaurant
    camis = Column(Integer)
    building = Column(Text)
    street = Column(Text)
    # Note: May have a - so best to leave as a string
    zip_code = Column(Text)
    boro = Column(Text)
    phone_number = Column(Text)
    # This data is an average, so unlike Inspection.numeric_grade, it is
    # a float
    numeric_grade = Column('grade', Float, nullable=True)

    cuisine_type = relationship('CuisineType', backref='restaurants')

    @property
    def address(self):
        return self.building + ' ' + self.street + ', ' + self.boro +\
            ' ' + self.zip_code

    def calculate_numeric_grade(self):
        grades = [
            float(inspection.numeric_grade) for inspection in self.inspections\
            if inspection.numeric_grade is not None
            ]

        if not grades:
            return None
        average = sum(grades)/len(grades)
        return average

    @property
    def grade(self):
        numeric_grade = self.numeric_grade
        if not numeric_grade:
            return None
        return Inspection.INT_TO_GRADE[self.numeric_grade]

class CuisineType(Base):
    __tablename__ = 'cuisine_type'

    name = Column(Text)

class Inspection(Base):
    __tablename__ = 'inspection'

    # Grades are given as letter grades, but stored as ints
    # I'm not quite sure what Z is meant to mean but it doesn't sound good
    GRADE_TO_INT = {
        'A': 5,
        'B': 4,
        # Score pending
        'N/A': 2,
        'C': 1
    }

    INT_TO_GRADE = {value: key for key, value in GRADE_TO_INT.items()}

    # Note: Will be stored as an int despite being a letter grade
    # If we were creating a full fledged product, _grade's __eq__,
    # __gt__, __ge__, __lt__, and __le__ would be best overwritten
    # to first convert letters to numbers, but not needed for MVP
    _numeric_grade = Column('grade', Integer, nullable=True)
    grade_date = Column(Date, nullable=True)
    _violation_code = Column('violation_code', Text, nullable=True)
    critical_flag = Column(Text)
    # TODO: Decide whether this is best as its own table
    # Represents what the nature of the inspection was, i.e. trans fat
    type = Column(Text)

    restaurant_id = Column(ForeignKey('restaurant.id'))
    restaurant = relationship('Restaurant', backref='inspections')

    @hybrid_property
    def grade(self):
        if not self.numeric_grade:
            return None

        return self.__class__.INT_TO_GRADE[self.numeric_grade]

    @grade.setter
    def grade(self, letter_grade):
        if not letter_grade:
            return
        self.numeric_grade = self.__class__.GRADE_TO_INT.get(
            letter_grade,
            self.__class__.GRADE_TO_INT['N/A'])

    @hybrid_property
    def violation_code(self):
        return self._violation_code

    @violation_code.setter
    def violation_code(self, violation_code):
        if not violation_code:
            violation_code = None
        self._violation_code = violation_code

    @hybrid_property
    def numeric_grade(self):
        return self._numeric_grade

    @numeric_grade.setter
    def numeric_grade(self, numeric_grade):
        self._numeric_grade = numeric_grade
        self.restaurant.numeric_grade = self.restaurant.calculate_numeric_grade()
