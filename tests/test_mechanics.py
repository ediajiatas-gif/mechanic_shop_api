import unittest
from app import create_app
from app.models import db, Mechanic, ServiceTicket

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name="Mech", email='mech@email.com', phone='123456789', salary=500000 )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
            self.mechanic_id = self.mechanic.id
        self.client = self.app.test_client()
            
    # Test GET all mechanics
    def test_get_mechanics(self):
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Mech")    
        
    # Test GET mechanic by ID
    def test_get_mechanic_by_id(self):
        response = self.client.get(f"/mechanics/1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "Mech")
        
    # Test Create Mechanic
    def test_create_mechanic(self):
        #defines dictionary containing data for new customer
        mechanic_payload = {
            "name": "Frank",
            'email': "frank@email.com",
            "phone": "123456789",
            "salary": 500000
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)   
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], "Frank")

    # Test UPDATE mechanic
    def test_update_mechanic(self):
        update_payload = {"salary": 60000}
        response = self.client.put(
            f"/mechanics/1",
            json=update_payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["salary"], 60000)
        
    # DELETE mechanic
    def test_delete_mechanic(self):
        response = self.client.delete(f"/mechanics/1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("successfully deleted", data["message"])

# Test return Mechanics in order of most tickets worked on
    def test_get_mechanics_by_ticket_count(self):
        from app.models import ServiceTicket, Mechanic

        # Setup DB objects inside app context
        with self.app.app_context():
            # Re-query existing mechanic
            mech1 = db.session.get(Mechanic, self.mechanic_id)

            # Create a second mechanic
            mech2 = Mechanic(name="Frank", email="frank@email.com", phone="987654321", salary=40000)
            db.session.add(mech2)
            db.session.commit()

            # Create service tickets
            ticket1 = ServiceTicket(vin="VIN123", service_desc="Fix brakes", customer_id=None)
            ticket2 = ServiceTicket(vin="VIN124", service_desc="Oil change", customer_id=None)
            ticket3 = ServiceTicket(vin="VIN125", service_desc="Tire rotation", customer_id=None)

            # Assign mechanics via the many-to-many relationship
            ticket1.mechanics.append(mech1)
            ticket2.mechanics.append(mech1)
            ticket3.mechanics.append(mech2)

            db.session.add_all([ticket1, ticket2, ticket3])
            db.session.commit()

        # Outside context: Make GET request to the route
        response = self.client.get("/mechanics/most_tickets")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)

        # The first mechanic should have the most tickets
        self.assertEqual(data[0]["name"], "Mech")
        self.assertEqual(len(data[0]["service_tickets"]), 2)
        self.assertEqual(data[1]["name"], "Frank")
        self.assertEqual(len(data[1]["service_tickets"]), 1)
        
    # Test Get Mechanic by Name
    def test_get_mechanic_by_name(self):
        response = self.client.get(f'/mechanics/search?name=Mech')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data[0]["name"], "Mech")