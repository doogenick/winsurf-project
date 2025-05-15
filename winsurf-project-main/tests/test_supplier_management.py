import pytest
from quote_system.database.models import Supplier, SupplierRate

class TestSupplierManagement:
    def test_create_supplier(self, client, session):
        # Test creating a new supplier
        response = client.post('/suppliers/new', data={
            'name': 'Test Supplier',
            'contact_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'services': 'Accommodation, Transfers'
        })
        
        assert response.status_code == 302
        supplier = Supplier.query.first()
        assert supplier is not None
        assert supplier.name == 'Test Supplier'

    def test_add_supplier_rate(self, client, session):
        # Create a test supplier
        supplier = Supplier(
            name='Test Supplier',
            contact_name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            services='Accommodation, Transfers'
        )
        session.add(supplier)
        session.commit()

        # Test adding a supplier rate
        response = client.post(f'/suppliers/{supplier.id}/rates/new', data={
            'service_type': 'Accommodation',
            'rate_type': 'Nightly',
            'rate_value': '100.00',
            'currency': 'USD',
            'season_start': '2025-05-01',
            'season_end': '2025-10-31',
            'min_group_size': '1',
            'max_group_size': '10'
        })
        
        assert response.status_code == 302
        rate = SupplierRate.query.first()
        assert rate is not None
        assert rate.rate_value == 100.00
        assert rate.currency == 'USD'
