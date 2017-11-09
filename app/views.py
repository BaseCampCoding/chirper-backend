import json
from http import HTTPStatus

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import auth

from app.models import ChirperUser


def JsonResponse(json_dumpable, status=HTTPStatus.OK):
    return HttpResponse(
        json.dumps(json_dumpable),
        content_type='application/json',
        status=status)


@require_POST
def signup(request: HttpRequest) -> HttpResponse:
    '''Signs up a new user.

    It expects a json payload with the following fields:
        - name
        - username
        - email
        - password

    Success Response:
        201, {}

    Failure Responses:
        400, {error: "MALFORMED_REQUEST"}
        422, {error: "INVALID_DATA", errors: <ValidationErrors>}
    '''
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'MALFORMED_REQUEST'
        }, HTTPStatus.BAD_REQUEST)

    try:
        chirper = ChirperUser.signup(name, username, email, password)
    except ValidationError as e:
        return JsonResponse({
            'error': 'INVALID_DATA',
            'errors': e.message_dict
        }, HTTPStatus.UNPROCESSABLE_ENTITY)

    return JsonResponse({}, HTTPStatus.CREATED)


def feed(request: HttpRequest, username: str) -> HttpResponse:
    try:
        chirper = ChirperUser.find_by_username(username)
    except ChirperUser.DoesNotExist:
        return JsonResponse({}, HTTPStatus.NOT_FOUND)
    paginator = Paginator(chirper.feed(), 25)
    page = request.GET.get('page')
    try:
        chirps = paginator.page(page)
    except PageNotAnInteger:
        chirps = paginator.page(1)
    except EmptyPage:
        chirps = paginator.page(paginator.num_pages)
    return JsonResponse({
        'chirper': {
            'name': chirper.name,
            'username': chirper.username,
            'description': chirper.description,
            'location': chirper.location,
            'website': chirper.website,
            'joined': {
                'month': chirper.joined.month,
                'year': chirper.joined.year
            }
        },
        'chirps': [{
            'author': {
                'name': c.author.name,
                'username': c.author.username
            },
            'date': {
                'month': c.date.month,
                'day': c.date.day,
                'year': c.date.year
            },
            'message': c.message
        } for c in chirps]
    }, 200)


@require_POST
def login(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'MALFORMED_REQUEST'
        }, HTTPStatus.BAD_REQUEST)

    try:
        username = data['username']
        password = data['password']
    except KeyError:
        return JsonResponse({
            'error': 'INVALID_DATA'
        }, HTTPStatus.UNPROCESSABLE_ENTITY)

    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return JsonResponse({}, HTTPStatus.CREATED)
    else:
        return JsonResponse({
            'error': 'INVALID_USERNAME_PASSWORD'
        }, HTTPStatus.UNAUTHORIZED)


@require_POST
def logout(request):
    auth.logout(request)
    return JsonResponse({})

def username_exists(request, username):
    return JsonResponse({'exists': ChirperUser.username_exists(username)})
