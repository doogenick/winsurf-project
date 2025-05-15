import pytest
from quote_system.database.models import Quote, SupplierBooking, OperationalNote

class TestBookingSystem:
    def test_add_supplier_booking(self, client, session):
        # Create a test quote
        quote = Quote(
            quote_number='QUOTE-0001',
            client_name='Test Client',
            start_date='2025-05-20',
            end_date='2025-05-25',
            group_size=2,
            margin_percentage=15.0,
            status='confirmed'
        )
        session.add(quote)
        session.commit()

        # Test adding supplier booking
        response = client.post(f'/bookings/{quote.id}/supplier-bookings/add', data={
            'supplier_id': '1',
            'status': 'confirmed',
            'booking_reference': 'TEST123',
            'notes': 'Test booking'
        })
        
        assert response.status_code == 302
        booking = SupplierBooking.query.first()
        assert booking is not None
        assert booking.status == 'confirmed'

    def test_add_operational_note(self, client, session):
        # Create a test quote
        quote = Quote(
            quote_number='QUOTE-0001',
            client_name='Test Client',
            start_date='2025-05-20',
            end_date='2025-05-25',
            group_size=2,
            margin_percentage=15.0,
            status='confirmed'
        )
        session.add(quote)
        session.commit()

        # Test adding operational note
        response = client.post(f'/bookings/{quote.id}/operational-notes/add', data={
            'note': 'Test operational note'
        })
        
        assert response.status_code == 302
        note = OperationalNote.query.first()
        assert note is not None
        assert note.note == 'Test operational note'
