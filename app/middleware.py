from app.models import ChirperUser
import json
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import AnonymousUser


def load_user_from_json_key(get_response):
    def middleware(request: HttpRequest) -> HttpResponse:
        try:
            data = json.loads(request.body.decode('utf-8'))
            key = data['key']
            request.user = ChirperUser.find_by_key(key)
        except (json.JSONDecodeError, KeyError, ChirperUser.DoesNotExist):
            request.user = AnonymousUser()
        except Exception as e:
            print(e)
        finally:
            return get_response(request)

    return middleware
