from __future__ import absolute_import
import api
import unittest
from flask import json
from mongoengine import connect


class ExperimentTestCase(unittest.TestCase):

    version_prefix = "/v1"

    def setUp(self):
        self.app = api.app.test_client()

    def post(self, uri, data):
        response = self.app.post(self.version_prefix + uri,
                                 data=json.dumps(data),
                                 content_type='application/json')
        return json.loads(response.data)

    def put(self, uri, data):
        response = self.app.put(self.version_prefix + uri,
                                data=json.dumps(data),
                                content_type='application/json')
        return json.loads(response.data)

    def get(self, uri):
        response = self.app.get(self.version_prefix + uri, content_type='application/json')
        return json.loads(response.data)

    def create_experiment(self, variant_choice="remember"):
        return self.post('/experiments',
                         {
                             "name": "Test flashcards",
                             "variant_choice": variant_choice,
                             "data": dict(flashcard=["123", "244"])
                         })

    def get_variant(self):
        return self.get('/variants/flashcard?user_id=21312')

    def update_variant(self, variant_id, success=True, data=""):
        return self.put('/variants/' + variant_id + '?user_id=21312',
                        dict(success=success, data=data))

    def test_create_experiment(self):
        response = self.create_experiment()
        self.assertEqual(len(response['variants']), 2)

    def test_get_variant_with_not_existing_user(self):
        self.create_experiment()
        response = self.get_variant()
        self.assertIn(response['data'], ["123", "244"])

    def test_get_variant_with_existing_user(self):
        self.create_experiment()
        first_response = self.get_variant()
        second_response = self.get_variant()
        self.assertIn(first_response['data'], second_response['data'])

    def test_update_variant_outcome(self):
        self.create_experiment()
        variant = self.get_variant()
        updated_variant = self.update_variant(variant['id'], success=True)
        self.assertEqual(updated_variant['successes'], 1)

    def test_update_forgotten_variant_outcome(self):
        self.create_experiment('forget')
        variant = self.get_variant()
        updated_variant = self.update_variant(variant['id'], success=True)
        self.assertEqual(updated_variant['successes'], 1)

    def tearDown(self):
        db = connect('applab')
        db.drop_database('applab')
