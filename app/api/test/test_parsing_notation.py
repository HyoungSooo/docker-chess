from django.test import TestCase, Client
import json
import unittest
from api.models import *


class TestParsing(unittest.TestCase):

    def setUp(self) -> None:
        self.c = Client()
