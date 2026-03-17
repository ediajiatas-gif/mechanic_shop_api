from app import create_app
from app.models import db, Inventory
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part = Inventory(part_name="test_part", price=50)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part)
            db.session.commit()
        self.client = self.app.test_client()


    # Test Create Part
    def test_create_part(self):
        #defines dictionary containing data for new part
        part_payload = {
            "part_name": "Oil Filter",
            "price": 30
        }
        #sends post request to inventories endpoint as JSON data
        response = self.client.post('/inventories/', json=part_payload)
        
        #verfies response code is 201, and part was added
        self.assertEqual(response.status_code, 201)
        
        #verfies that returned JSON contains expected name for new part
        data = response.get_json()
        self.assertEqual(data['part_name'], "Oil Filter")
