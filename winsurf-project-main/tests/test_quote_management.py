import pytest
from quote_system.database.models import Quote, Activity

class TestQuoteManagement:
    def test_create_quote(self, client, session):
        # Test creating a new quote
        response = client.post('/quotes/new', data={
            'client_name': 'Test Client',
            'start_date': '2025-05-20',
            'end_date': '2025-05-25',
            'group_size': '2',
            'margin_percentage': '15.0',
            'activity_count': '1',
            'activity_name_0': 'Test Activity',
            'activity_description_0': 'Test description',
            'activity_cost_0': '100.00',
            'activity_duration_0': '2'
        })
        
        assert response.status_code == 302
        quote = Quote.query.first()
        assert quote is not None
        assert quote.client_name == 'Test Client'
        assert len(quote.activities) == 1

    def test_list_quotes(self, client, session):
        # Create a test quote
        quote = Quote(
            quote_number='QUOTE-0001',
            client_name='Test Client',
            start_date='2025-05-20',
            end_date='2025-05-25',
            group_size=2,
            margin_percentage=15.0,
            status='draft'
        )
        session.add(quote)
        session.commit()

        # Test listing quotes
        response = client.get('/quotes')
        assert response.status_code == 200
        assert b'Test Client' in response.data

    def test_edit_quote(self, client, session):
        # Create a test quote
        quote = Quote(
            quote_number='QUOTE-0001',
            client_name='Test Client',
            start_date='2025-05-20',
            end_date='2025-05-25',
            group_size=2,
            margin_percentage=15.0,
            status='draft'
        )
        session.add(quote)
        session.commit()

        # Test editing the quote
        response = client.post(f'/quotes/{quote.id}/edit', data={
            'client_name': 'Updated Client',
            'start_date': '2025-05-20',
            'end_date': '2025-05-25',
            'group_size': '2',
            'margin_percentage': '15.0'
        })
        
        assert response.status_code == 302
        updated_quote = Quote.query.get(quote.id)
        assert updated_quote.client_name == 'Updated Client'
