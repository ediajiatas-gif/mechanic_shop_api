from app import create_app
from app.models import db, ServiceTicket, Mechanic, Inventory, Customer
from app.utils.util import encode_token
import unittest
from datetime import datetime

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Customer
            self.customer = Customer(name="Test Customer", email="cust@test.com", phone="555-0000", password='123')
            db.session.add(self.customer)
            db.session.commit()
            # fetch the id while in the session
            self.customer_id = self.customer.id
            
            # Service Ticket
            self.ticket = ServiceTicket(
                vin="12345678",
                service_desc="Oil Change",
                customer_id=self.customer_id,
                service_date=datetime.utcnow()
            )
            
            # Mechanic
            self.mechanic = Mechanic(name="Mech", email="mech@email.com", phone="555-1111", salary=50000)
            
            # Inventory
            self.part = Inventory(part_name="Oil Filter", price=10)

            db.session.add_all([self.ticket, self.mechanic, self.part])
            db.session.commit()

            # Link ticket relationships
            self.ticket.mechanics.append(self.mechanic)
            self.ticket.inventory.append(self.part)
            db.session.commit()
            self.ticket_id = self.ticket.id
            self.mechanic_id = self.mechanic.id

        self.client = self.app.test_client()

    # Test Get All Tickets
    def test_get_tickets(self):
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # Test Create Ticket
    def test_create_ticket(self):
        payload = {
            "vin": "87654321",
            "service_desc": "Brake Check",
            "customer_id": self.customer_id,
        }
        response = self.client.post('/service-tickets/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['vin'], "87654321")

    # Test Assign mechanic
    def test_assign_new_mechanic(self):
        with self.app.app_context():
            # Create a new mechanic to assign
            new_mech = Mechanic(
                name="New Mech", email="newmech@test.com", phone="555-2222", salary=55000
            )
            db.session.add(new_mech)
            db.session.commit()
            new_mech_id = new_mech.id

        response = self.client.put(f'/service-tickets/{self.ticket_id}/assign-mechanic/{new_mech_id}')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('mechanics', data)
        mechanic_ids = data['mechanics'] if isinstance(data['mechanics'], list) else []
        self.assertIn(new_mech_id, mechanic_ids)
        
    # Test Remove Mechanic from ticket
    def test_remove_mechanic_from_ticket(self):

        response = self.client.put(
            f'/service-tickets/{self.ticket_id}/remove-mechanic/{self.mechanic_id}'
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('mechanics', data)

        # mechanics is a list of IDs in your schema
        mechanic_ids = data['mechanics'] if isinstance(data['mechanics'], list) else []
        self.assertNotIn(self.mechanic_id, mechanic_ids)

    # Test Edit Ticket 
    def test_edit_ticket(self):
        update_payload = {"service_desc": "Updated Service"}
        response = self.client.put(f'/service-tickets/{self.ticket.id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['service_desc'], "Updated Service")

    def test_add_part_to_ticket_success(self):
        with self.app.app_context():
            # Create a new part to add
            new_part = Inventory(part_name="Brake Pad", price=25)
            db.session.add(new_part)
            db.session.commit()
            new_part_id = new_part.id

        # Call the route to add the part
        response = self.client.put(f'/service-tickets/{self.ticket_id}/add-part/{new_part_id}')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('inventory', data)  # inventory is the parts list
        part_ids = data['inventory'] if isinstance(data['inventory'], list) else []
        self.assertIn(new_part_id, part_ids)
        
