import unittest
import sys
import os
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quote_system.app.quoting.pricing_engine import QuoteEngine

class TestComprehensiveScenarios(unittest.TestCase):
    """Test suite for comprehensive end-to-end quote scenarios"""
    
    def setUp(self):
        self.engine = QuoteEngine()
        self.today = date.today()
        
    def test_8pax_camping_tour(self):
        """Test scenario 1: 8-pax camping tour with truck meals
        
        This matches Excel 'Itinerary' tab calculations for a standard camping tour
        with game drives, hikes, and truck meals.
        """
        # Test parameters
        inputs = {
            "pax": 8,
            "days": 5,
            "start_date": self.today,
            "end_date": self.today + timedelta(days=5),
            "meals": ["truck", "truck", "lodge", "own", "truck"],
            "activities": [
                {"type": "game_drive", "cost": 350, "quantity": 2},
                {"type": "hike", "cost": 200, "quantity": 1}
            ],
            "accommodation": {
                "type": "camping",
                "cost_per_night": 135
            },
            "truck": {
                "type": "nomad", 
                "cost_per_day": 1403.56
            },
            "meal_cost": {
                "truck": 50,
                "lodge": 120,
                "own": 0
            }
        }
        
        # Calculate expected values
        expected_accommodation = inputs["accommodation"]["cost_per_night"] * inputs["days"] * inputs["pax"]
        expected_activities = ((inputs["activities"][0]["cost"] * inputs["activities"][0]["quantity"]) + 
                             (inputs["activities"][1]["cost"] * inputs["activities"][1]["quantity"])) * inputs["pax"]
        expected_truck = inputs["truck"]["cost_per_day"] * inputs["days"]
        
        # Calculate meals based on plan
        expected_meals = 0
        for meal_type in inputs["meals"]:
            expected_meals += inputs["meal_cost"][meal_type] * inputs["pax"]
            
        # Note: in the real Excel sheet, meals would be for all days
        # This test simplifies by providing specific meal types per day
        
        # Formula-based total
        expected_total = expected_accommodation + expected_activities + expected_truck + expected_meals
        
        # Create charges based on inputs
        charges = [
            {
                "type": "fixed",
                "value": 0,
                "days": inputs["days"],
                "quantity": inputs["pax"],
                "formula": f"={inputs['accommodation']['cost_per_night']}*days*quantity"  # Accommodation
            },
            {
                "type": "fixed",
                "value": 0,
                "quantity": inputs["pax"],
                "formula": f"={(inputs['activities'][0]['cost'] * inputs['activities'][0]['quantity'] + inputs['activities'][1]['cost'] * inputs['activities'][1]['quantity'])}*quantity"  # Activities
            },
            {
                "type": "fixed",
                "value": 0,
                "days": inputs["days"],
                "formula": f"={inputs['truck']['cost_per_day']}*days"  # Truck
            },
            {
                "type": "fixed",
                "value": 0,
                "quantity": inputs["pax"],
                "formula": "=50*3*quantity+120*1*quantity"  # 3 truck meals + 1 lodge meal
            }
        ]
        
        # Calculate with the engine
        total = self.engine._calculate_complex_cost(
            inputs["accommodation"]["cost_per_night"],  # base_cost
            1.0,  # seasonal_factor (no adjustment for this test)
            inputs["pax"],  # group_size
            charges
        )
        
        print(f"Expected total: {expected_total}")
        print(f"Actual total: {total}")
        
        # Assert results match Excel calculations
        self.assertAlmostEqual(total, expected_total, places=2)
        
    def test_4pax_lodge_with_seasonal_markup(self):
        """Test scenario 2: 4-pax luxury lodge tour with seasonal markup and currency conversion"""
        # Test parameters
        inputs = {
            "pax": 4,
            "days": 7,
            "start_date": date(2025, 1, 15),  # High season
            "end_date": date(2025, 1, 22),
            "accommodation": {
                "type": "lodge",
                "cost_per_night": 2200
            },
            "activities": [
                {"type": "wine_tasting", "cost": 450, "quantity": 1},
                {"type": "safari", "cost": 1200, "quantity": 1}
            ],
            "seasonal_factor": 1.15,  # 15% high season markup
            "exchange_rate": 18.0  # ZAR to USD
        }
        
        # Calculate expected values with markup
        lodge_cost = inputs["accommodation"]["cost_per_night"] * inputs["days"] * inputs["pax"]
        activities_cost = ((inputs["activities"][0]["cost"] * inputs["activities"][0]["quantity"]) + 
                          (inputs["activities"][1]["cost"] * inputs["activities"][1]["quantity"])) * inputs["pax"]
        
        # Total in ZAR with seasonal markup
        expected_total_zar = (lodge_cost + activities_cost) * inputs["seasonal_factor"]
        
        # Convert to USD
        expected_total_usd = expected_total_zar / inputs["exchange_rate"]
        
        # Create charges for calculation
        charges = [
            {
                "type": "fixed",
                "value": 0,
                "days": inputs["days"],
                "quantity": inputs["pax"],
                "formula": f"={inputs['accommodation']['cost_per_night']}*days*quantity*seasonal"  # Lodge with seasonal factor
            },
            {
                "type": "fixed",
                "value": 0,
                "quantity": inputs["pax"],
                "formula": f"={(inputs['activities'][0]['cost'] * inputs['activities'][0]['quantity'] + inputs['activities'][1]['cost'] * inputs['activities'][1]['quantity'])}*quantity*seasonal"  # Activities with seasonal factor
            }
        ]
        
        # Calculate with the engine
        total_zar = self.engine._calculate_complex_cost(
            inputs["accommodation"]["cost_per_night"],  # base_cost
            inputs["seasonal_factor"],  # seasonal_factor
            inputs["pax"],  # group_size
            charges
        )
        
        # Convert to USD
        total_usd = total_zar / inputs["exchange_rate"]
        
        print(f"Expected total ZAR: {expected_total_zar}")
        print(f"Actual total ZAR: {total_zar}")
        print(f"Expected total USD: {expected_total_usd}")
        print(f"Actual total USD: {total_usd}")
        
        # Assert results match expected calculations
        self.assertAlmostEqual(total_zar, expected_total_zar, places=2)
        self.assertAlmostEqual(total_usd, expected_total_usd, places=2)
    
    def test_invalid_inputs(self):
        """Test scenario 3: Invalid inputs handling"""
        # Test with invalid number of passengers (0)
        with self.assertRaises(ValueError):
            self.engine._calculate_complex_cost(
                100,  # base_cost
                1.0,  # seasonal_factor
                0,    # invalid group_size (should raise error)
                []
            )
            
        # Test with invalid seasonal factor (negative)
        with self.assertRaises(ValueError):
            self.engine._calculate_complex_cost(
                100,  # base_cost
                -0.5,  # invalid seasonal_factor (should raise error)
                4,     # group_size
                []
            )
            
        # Test formula parser with invalid formula
        result = self.engine.formula_parser.parse("=invalid_formula", {"base": 100})
        self.assertEqual(result, 0.0)  # Should fail gracefully with 0
        
    def test_crew_park_fee_allocation(self):
        """Test scenario 4: Crew park fee allocation across passengers"""
        # Test parameters
        inputs = {
            "pax": 6,  # 6 passengers
            "crew": 2,  # 2 crew members
            "park_fee": 200,  # Per person park entrance fee
            "crew_allocation": "split"  # Crew costs split across passengers
        }
        
        # Calculate expected values
        passenger_fees = inputs["pax"] * inputs["park_fee"]
        crew_fees = inputs["crew"] * inputs["park_fee"]
        
        # When crew costs are split across passengers
        crew_fee_per_passenger = crew_fees / inputs["pax"]
        
        # Each passenger pays their fee + portion of crew fees
        expected_per_passenger = inputs["park_fee"] + crew_fee_per_passenger
        expected_total = passenger_fees + crew_fees
        
        # Create charges for calculation
        charges = [
            {
                "type": "fixed",
                "value": 0,
                "quantity": inputs["pax"],
                "formula": f"={inputs['park_fee']}*quantity"  # Passenger fees
            },
            {
                "type": "fixed",
                "value": 0,
                "formula": f"={inputs['crew']}*{inputs['park_fee']}"  # Crew fees
            }
        ]
        
        # Calculate with the engine
        total = self.engine._calculate_complex_cost(
            0,  # base_cost (not relevant for this test)
            1.0,  # seasonal_factor (no adjustment)
            inputs["pax"],  # group_size
            charges
        )
        
        # Calculate per passenger cost
        per_passenger = total / inputs["pax"]
        
        print(f"Expected total: {expected_total}")
        print(f"Actual total: {total}")
        print(f"Expected per passenger: {expected_per_passenger}")
        print(f"Actual per passenger: {per_passenger}")
        
        # Assert results match expected calculations
        self.assertAlmostEqual(total, expected_total, places=2)
        self.assertAlmostEqual(per_passenger, expected_per_passenger, places=2)

if __name__ == '__main__':
    unittest.main()
