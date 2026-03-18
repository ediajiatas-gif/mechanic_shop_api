from app import create_app
from app.models import db, Customer, ServiceTicket
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create test customer
            member = Customer(
                name="test_user",
                email="test@email.com",
                phone="800-111-1212",
                password='test'
            )
            db.session.add(member)
            db.session.commit()

            # Save the ID for all tests
            self.member_id = member.id
        self.token = encode_token(self.member_id)
        
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

    # Test Get Tickets for Authenticated Customer
    def test_get_my_tickets(self):
        with self.app.app_context():
            ticket1 = ServiceTicket(
                vin="123ABC",
                service_desc="Oil change",
                customer_id=1
            )
            ticket2 = ServiceTicket(
                vin="456DEF",
                service_desc="Brake repair",
                customer_id=1
            )

            db.session.add_all([ticket1, ticket2])
            db.session.commit()

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = self.client.get("/customers/my-tickets", headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["service_desc"], "Oil change")
        self.assertEqual(data[1]["service_desc"], "Brake repair")

    # Test GET all Customers
    def test_get_customers(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "test_user")    
        
    # Test GET Customer by ID
    def test_get_customer_by_id(self):
        response = self.client.get(f"/customers/1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "test_user")

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

    # Test Deleting the authenticated customer
    def test_delete_customer(self):
        # Generate token for existing customer
        token = encode_token(self.member_id)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Call the DELETE endpoint
        response = self.client.delete("/customers/", headers=headers)

        # Check response status
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("successfully deleted", data['message'])

        # Verify the customer is actually deleted from DB
        with self.app.app_context():
            deleted_customer = db.session.get(Customer, self.member_id)
            self.assertIsNone(deleted_customer)