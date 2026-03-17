from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        # Create Instance of Customer
        self.member = Customer(name="test_user", email="test@email.com", phone="800-111-1212", password='test')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.member)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
        
    # Test Create Customer 
    def test_create_customer(self):
        #defines dictionary containing data for new customer
        customer_payload = {
            "name": "John Doe",
            "email": "johndoe@email.com",
            "phone": "415-901-5991",
            "password": "123"
        }
        #sends post request to customers endpoint as JSON data
        response = self.client.post('/customers/', json=customer_payload)
        
        #verfies response code is 201, and customer was added
        self.assertEqual(response.status_code, 201)
        
        #verfies that returned JSON contains expected name for new customer
        data = response.get_json()
        self.assertEqual(data['name'], "John Doe")

    # Test for Invalid Customer
    def test_invalid_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "johndoe@email.com",
            "phone": "415-901-5991",
        }
        response = self.client.post('/customers/', json=customer_payload)
        
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertEqual(data['password'], ['Missing data for required field.'])

    
    # Test Login Customer
    def test_login_member(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        data = response.get_json()
        self.assertIn('token', data)
    
    # Test Invalid Login    
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')
        
    # Test Update Member
    def test_update_member(self):

        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        login_response = self.client.post('/customers/login', json=credentials)
        token = login_response.get_json()['token']

        headers = {
            'Authorization': f'Bearer {token}'
        }

        update_payload = {
            "name": "updated_user"
        }

        response = self.client.put('/customers/1', json=update_payload, headers=headers)

        self.assertEqual(response.status_code, 200)