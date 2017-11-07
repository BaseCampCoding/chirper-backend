import json
from http import HTTPStatus

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

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
