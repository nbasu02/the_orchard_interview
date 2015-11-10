from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Restaurant,
    CuisineType
    )


@view_config(route_name='home',
    renderer='neilbasu_theorchard:templates/thai_food.html.mako')
def show_thai_restaurants(request):
    restaurants = DBSession.query(Restaurant).join(
        CuisineType, Restaurant.cuisine_type_id==CuisineType.id
        ).filter(
        CuisineType.name=='Thai'
        ).order_by(Restaurant.numeric_grade.desc()).limit(10).all()
    return {
        'restaurants': restaurants,
        'request': request}
