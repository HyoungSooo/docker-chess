from django.test import TestCase, Client
import json
import unittest
from api.models import *


class TestParsing(unittest.TestCase):

    def setUp(self) -> None:
        self.c = Client()

    def client_login(self):
        self.c.login(username='test', password='test123')

    def test_api_login_user_upload_success(self):
        self.c.login(username='test', password='test123')
        op = open('api\\test\\test.txt', 'r')
        res = self.c.post('http://127.0.0.1:8000/api/uploadfile',
                          data={'uploaded_file': op})

        self.assertEqual(res.status_code, 200)

        with open('api\\test\\test.txt') as fp:
            file1_contents = fp.read()

        with open('api\\dist\\notation\\test.txt') as fp:
            file2_contents = fp.read()

        self.assertEqual(len(file1_contents), len(file2_contents))
        self.assertEqual(json.loads(res.content), 'test.txt')

    def test_unauth_user_upload_fail(self):

        op = open('api\\test\\test.txt', 'r')
        res = self.c.post('http://127.0.0.1:8000/api/uploadfile',
                          data={'uploaded_file': op})

        self.assertEqual(res.status_code, 401)

    def test_parsing_notation_data(self):
        self.client_login()

        op = open('api\\dist\\notation\\v1.pgn', 'rb')

        filename = json.loads(self.c.post(
            'http://127.0.0.1:8000/api/uploadfile', data={'uploaded_file': op}).content)

        res = self.c.get(
            f'http://127.0.0.1:8000/api/parse?filename={filename}&num=5')

        self.assertEqual(res.status_code, 200)

        data = ChessNotation.objects.all()

        self.assertEqual(len(data), 5)

        self.c.logout()

    def test_get_data(self):
        res = self.c.get(f'http://127.0.0.1:8000/api/getdata')

        self.assertEqual(res.status_code, 401)

        self.client_login()

        res = self.c.get(f'http://127.0.0.1:8000/api/getdata')

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.content)

        self.assertEqual(len(data), len(ChessNotation.objects.all()))
