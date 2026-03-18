from app import create_app
from app.models import db, Inventory
from app.utils.util import encode_token
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        # Create Instance of Part
        self.part = Inventory(part_name="test_part", price=50.0)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    # Get all Parts
    def test_get_parts(self):
        response = self.client.get('/inventories/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # Test Create Part
    def test_create_part(self):
        #defines dictionary containing data for new customer
        part_payload = {
            "part_name": "Brake Pad",
            'price': 80.0
        }

        response = self.client.post('/inventories/', json=part_payload)   
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['part_name'], "Brake Pad")

    # Update Part
    def test_update_part(self):
        update_payload = {"price": 15.0}
        response = self.client.put(f'/inventories/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['price'], 15.0)

    # Delete Part
    def test_delete_part(self):
        response = self.client.delete(f'/inventories/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully deleted", response.get_json()["message"])