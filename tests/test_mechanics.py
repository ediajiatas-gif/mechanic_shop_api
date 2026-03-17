from app import create_app
from app.models import db, Mechanic
from app.utils.util import encode_token
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        # Create Instance of Mechanic
        self.mechanic = Mechanic(name="test_mechanic", email="mechanic@email.com", phone="800-111-1212", salary=500000)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    # Test Create Mechanic 
    def test_create_mechanic(self):
        #defines dictionary containing data for new mechanic
        mechanic_payload = {
            "name": "John Doe",
            "email": "johndoe@email.com",
            "phone": "415-901-5991",
            "salary": 100000
        }
        #sends post request to mechanics endpoint as JSON data
        response = self.client.post('/mechanics/', json=mechanic_payload)
        
        #verfies response code is 201, and mechanic was added
        self.assertEqual(response.status_code, 201)
        
        #verfies that returned JSON contains expected name for new mechanic
        data = response.get_json()
        self.assertEqual(data['name'], "John Doe")

    # Test for Invalid Mechanic
    def test_invalid_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "johndoe@email.com",
            "phone": "415-901-5991",
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertEqual(data['salary'], ['Missing data for required field.'])