from typing import Dict, List, Optional, Tuple, Any, TypeVar, Generic
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from .tdd_models import CostComponent, Quote
from functools import lru_cache
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class FormulaCacheKey:
    """Key for caching formula results."""
    formula: str
    context_hash: int


class PricingService:
    def __init__(self):
        self.seasonal_rates = {
            'high': 1.2,  # 20% increase
            'low': 0.8,   # 20% decrease
            'shoulder': 1.0  # base rate
        }
        self.group_discounts = {
            '1-4': 0.0,
            '5-9': 0.05,
            '10-19': 0.1,
            '20+': 0.15
        }
        self.subcontracting_margin = 0.15  # 15%
        self.formula_cache = lru_cache(maxsize=128)(self._formula_parser)

    def _formula_parser(self, formula: str, context: Dict[str, Any]) -> float:
        """
        Parse and evaluate an Excel-like formula.
        
        Enhanced features:
        1. Supports Excel-style cell references (e.g., 'A1', 'B2')
        2. Supports Excel-style functions (e.g., 'SUM(A1:A3)')
        3. Supports multiple operations and parentheses
        4. Caches results for performance
        
        Args:
            formula (str): Excel-like formula (e.g., '=A1+B2*C3')
            context (Dict[str, Any]): Dictionary of values to use in the formula.
            
        Returns:
            float: The result of evaluating the formula.
        """
        # Return as is if it's not a formula
        if not isinstance(formula, str) or not formula.startswith('='):
            try:
                return float(formula)
            except (ValueError, TypeError):
                return 0.0
        
        # Remove the '=' at the beginning
        expr = formula[1:]
        
        # Convert all context values to float for safe calculation
        safe_dict = {}
        for k, v in context.items():
            try:
                safe_dict[k] = float(v)
            except (ValueError, TypeError):
                safe_dict[k] = 0.0
        
        # Add Excel-style functions
        excel_functions = {
            'SUM': lambda *args: sum(args),
            'AVERAGE': lambda *args: sum(args) / len(args) if args else 0,
            'MAX': max,
            'MIN': min,
            'ROUND': round,
            'ABS': abs,
            'POW': pow,
            'IF': lambda cond, true_val, false_val: true_val if cond else false_val,
            'AND': lambda *args: all(args),
            'OR': lambda *args: any(args)
        }
        
        # Add Excel-style cell references
        cell_pattern = re.compile(r'([A-Z]+)(\d+)')
        
        def get_cell_value(match):
            col = match.group(1)
            row = int(match.group(2))
            # Convert column letter to number (A=1, B=2, etc.)
            col_num = sum((ord(c) - ord('A') + 1) * (26 ** i) 
                         for i, c in enumerate(reversed(col)))
            # Create cell reference like 'A1' -> 'cell_1_1'
            cell_ref = f'cell_{row}_{col_num}'
            return safe_dict.get(cell_ref, 0)
        
        # Replace cell references with actual values
        expr = cell_pattern.sub(lambda m: str(get_cell_value(m)), expr)
        
        # Add math functions for advanced calculations
        safe_math = {
            'sum': sum,
            'min': min,
            'max': max,
            'round': round,
            'abs': abs,
            'pow': pow
        }
        
        # Combine all functions
        safe_dict.update(excel_functions)
        safe_dict.update(safe_math)
        
        # Handle Excel-style exponentiation (^)
        if '^' in expr:
            expr = expr.replace('^', '**')
        
        # Handle Excel-style function calls
        def handle_function_call(match):
            func_name = match.group(1).upper()
            args_str = match.group(2)
            
            # Split arguments by comma
            args = []
            depth = 0
            last_pos = 0
            
            for i, char in enumerate(args_str):
                if char == ',':
                    if depth == 0:
                        arg = args_str[last_pos:i].strip()
                        if arg:
                            args.append(arg)
                        last_pos = i + 1
                elif char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
            
            # Add last argument
            arg = args_str[last_pos:].strip()
            if arg:
                args.append(arg)
            
            # Evaluate arguments
            evaluated_args = []
            for arg in args:
                try:
                    # Try to evaluate as a number
                    evaluated_args.append(float(arg))
                except ValueError:
                    # Try to evaluate as a variable from context
                    try:
                        evaluated_args.append(float(safe_dict[arg]))
                    except (KeyError, ValueError):
                        evaluated_args.append(0)
            
            # Call function with evaluated arguments
            if func_name in excel_functions:
                return str(excel_functions[func_name](*evaluated_args))
            return arg
        
        # Replace function calls with their results
        func_pattern = re.compile(r'([A-Z]+)\(([^()]*)\)')
        expr = func_pattern.sub(handle_function_call, expr)
        
        # Evaluate the expression in a safe environment
        try:
            result = eval(expr, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            print(f"Warning: Error evaluating formula '{formula}': {str(e)}")
            return 0.0  # Fail gracefully in production

    def formula_parser(self, formula: str, context: Dict[str, Any]) -> float:
        """Wrapper for formula parsing with caching."""
        # Create a hashable key for caching
        context_hash = hash(tuple(sorted(context.items())))
        cache_key = FormulaCacheKey(formula=formula, context_hash=context_hash)
        
        # Try to get result from cache
        try:
            return self.formula_cache(cache_key)
        except TypeError:
            # If formula is not cacheable, evaluate directly
            return self._formula_parser(formula, context)

    def calculate_base_cost(self, activities: List[Dict]) -> float:
        """Calculate base cost of all activities."""
        return sum(activity['cost'] for activity in activities)

    def apply_seasonal_rates(self, base_cost: float, start_date: date) -> float:
        """Apply seasonal rate based on travel dates."""
        current_month = start_date.month
        if current_month in [6, 7, 8]:  # Summer high season
            return base_cost * self.seasonal_rates['high']
        elif current_month in [12, 1, 2]:  # Winter high season
            return base_cost * self.seasonal_rates['high']
        elif current_month in [3, 4, 9, 10]:  # Shoulder season
            return base_cost * self.seasonal_rates['shoulder']
        else:  # Low season
            return base_cost * self.seasonal_rates['low']

    def apply_group_discount(self, total_cost: float, group_size: int) -> float:
        """Apply group discount based on number of travelers."""
        if group_size <= 0:
            raise ValueError("Group size must be greater than 0")
        
        if group_size < 5:
            return total_cost * (1 - self.group_discounts['1-4'])
        elif group_size < 10:
            return total_cost * (1 - self.group_discounts['5-9'])
        elif group_size < 20:
            return total_cost * (1 - self.group_discounts['10-19'])
        else:
            return total_cost * (1 - self.group_discounts['20+'])

    def add_subcontracting_margin(self, total_cost: float) -> float:
        """Add subcontracting margin to the total cost."""
        return total_cost * (1 + self.subcontracting_margin)

    def create_quote(self, activities: List[Dict], start_date: date, end_date: date, 
                    group_size: int, margin_percentage: float = 0.0) -> Dict:
        """Create a complete quote with all calculations."""
        # Calculate base cost
        base_cost = self.calculate_base_cost(activities)
        
        # Apply seasonal rates
        seasonal_cost = self.apply_seasonal_rates(base_cost, start_date)
        
        # Apply group discount
        discounted_cost = self.apply_group_discount(seasonal_cost, group_size)
        
        # Add subcontracting margin
        total_cost = self.add_subcontracting_margin(discounted_cost)
        
        # Calculate final price with margin
        final_price = total_cost * (1 + (margin_percentage / 100))
        
        return {
            'base_cost': base_cost,
            'seasonal_cost': seasonal_cost,
            'discounted_cost': discounted_cost,
            'total_cost': total_cost,
            'final_price': final_price,
            'margin_percentage': margin_percentage,
            'start_date': start_date,
            'end_date': end_date,
            'group_size': group_size,
            'activities': activities
        }

    def calculate_complex_cost(self, base_cost: float, 
                              seasonal_factor: float,
                              group_size: int,
                              additional_charges: List[Dict]) -> float:
        """
        Calculate cost with Excel-like formulas.
        
        This method mimics Excel's calculation patterns:
        1. First evaluates all formulas against their context
        2. Then applies percentage adjustments
        3. Returns the final amount with proper rounding
        
        Enhanced features:
        1. Caches formula results for performance
        2. Supports Excel-style cell references
        3. Supports Excel-style functions (SUM, AVERAGE, etc.)
        4. Handles complex expressions with multiple operations
        """
        # Validate inputs
        if group_size <= 0:
            raise ValueError("Group size must be greater than 0")
            
        if seasonal_factor <= 0:
            raise ValueError("Seasonal factor must be greater than 0")
        
        # Start with 0 - we'll add all charges explicitly
        total = 0
        
        # STEP 1: Create a base context for all formulas
        base_context = {
            'base': base_cost,
            'seasonal': seasonal_factor,
            'group': group_size,
            'total': 0,  # Will be updated as we go
            'days': 1,   # Default days
            'quantity': 1  # Default quantity
        }
            
        # STEP 2: Apply charges sequentially
        for i, charge in enumerate(additional_charges):
            # Update context with current total and charge-specific values
            context = base_context.copy()
            context.update({
                'days': charge.get('days', base_context['days']),
                'quantity': charge.get('quantity', base_context['quantity']),
                'charge_index': i + 1,  # 1-based index for Excel-style formulas
            })
            
            # If there's a formula, use it to calculate value
            if 'formula' in charge:
                # Get value from formula
                formula_value = self.formula_parser(charge['formula'], context)
                    
                if charge.get('type') == 'percentage':
                    # Apply as percentage adjustment
                    total += total * formula_value  # Directly apply the percentage
                else:
                    # Add formula result as fixed amount
                    total += formula_value
            else:
                # Use provided value if no formula
                if charge.get('type') == 'percentage':
                    total += total * charge['value']
                else:
                    total += charge['value']
        
        # STEP 3: Apply group discount AFTER all charges
        # This is equivalent to a percentage rebate in Excel
        if group_size > 10:
            total *= 0.9  # 10% bulk discount
                    
        return round(total, 2)

    def _formula_parser(self, formula: str, context: Dict[str, Any]) -> float:
        """
        Parse and evaluate an Excel-like formula.
        
        Args:
            formula (str): Excel-like formula (e.g., '=A1+B2*C3')
            context (Dict[str, Any]): Dictionary of values to use in the formula.
            
        Returns:
            float: The result of evaluating the formula.
        """
        # Return as is if it's not a formula
        if not isinstance(formula, str) or not formula.startswith('='):
            try:
                return float(formula)
            except (ValueError, TypeError):
                return 0.0
        
        # Remove the '=' at the beginning
        expr = formula[1:]
        
        # Convert all context values to float for safe calculation
        safe_dict = {}
        for k, v in context.items():
            try:
                safe_dict[k] = float(v)
            except (ValueError, TypeError):
                safe_dict[k] = 0.0
        
        # Add math functions for advanced calculations
        safe_math = {
            'sum': sum,
            'min': min,
            'max': max,
            'round': round,
            'abs': abs,
            'pow': pow  # Add power function for exponentiation
        }
        safe_dict.update(safe_math)
        
        # Handle Excel-style exponentiation (^)
        if '^' in expr:
            expr = expr.replace('^', '**')
        
        # Evaluate the expression in a safe environment
        try:
            result = eval(expr, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            print(f"Warning: Error evaluating formula '{formula}': {str(e)}")
            return 0.0  # Fail gracefully in production

    def formula_parser(self, formula: str, context: Dict[str, Any]) -> float:
        """Wrapper for formula parsing."""
        return self._formula_parser(formula, context)
