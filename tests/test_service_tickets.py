from app import create_app
from app.models import db, ServiceTicket
import unittest

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.ticket = ServiceTicket(vin="12345678", service_desc="Oil Change")

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.ticket)
            db.session.commit()
        self.client = self.app.test_client()


    # Test Create Ticket
    def test_create_ticket(self):
        #defines dictionary containing data for new ticket
        ticket_payload = {
            "vin": "12345678",
            "service_desc": "Oil Changed"
        }
        #sends post request to service-tickets endpoint as JSON data
        response = self.client.post('/service-tickets/', json=ticket_payload)
        
        #verfies response code is 201, and part was added
        self.assertEqual(response.status_code, 201)
        
        #verfies that returned JSON contains expected name for new part
        data = response.get_json()
        self.assertEqual(data['vin'], "12345678")
