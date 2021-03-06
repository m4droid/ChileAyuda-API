# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test.testcases import TransactionTestCase
from rest_framework.test import APIClient


class TestViewSetIncident(TransactionTestCase):

    fixtures = [
        'regions.json',
        'provinces.json',
        'communes.json',
        'coordinates.json',
        'users.json',
        'incidents.json'
    ]

    def setUp(self):
        super(TestViewSetIncident, self).setUp()
        self.client = APIClient()

    def test_http_get(self):
        response = self.client.get('/0/incidents/')

        data = json.loads(response.content)

        self.assertEquals(200, response.status_code)
        self.assertEquals(1, len(data))
        self.assertEquals(
            {'id': 1, 'latitude': -33.4583573, 'longitude': -70.6631088},
            data[0]['coordinates']
        )
