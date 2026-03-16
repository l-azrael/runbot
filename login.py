from requests import request

from core.fixture import BaseLogin


class Login(BaseLogin):

    def login(self) -> dict:
        resp_login = {}
        return resp_login

    def make_headers(self, resp_login: dict) -> dict:
        headers = {
            'token': f's-web-5472c31410987e12ee2ae626f1e378a9'}
        return headers
