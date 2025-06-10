from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, ValidationError
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Default values for the form
DEFAULT_VALUES = {
    'total_shares': 1000000,
    'founder1_percentage': 30.0,
    'founder2_percentage': 30.0,
    'founder3_percentage': 15.0,
    'founder4_percentage': 7.5,
    'founder5_percentage': 14.3,
    'options_pool': 3.2,
    'seed_amount': 6000000,
    'seed_valuation': 30000000,  # 5x investment
    'series_a_amount': 50000000,
    'series_a_valuation': 200000000,  # 4x investment
    'exit_amount': 400000000
}

# Tax rates for different tax types
TAX_RATES = {
    'individual': 0.33,  # 33% for individuals
    'company': 0.23     # 23% for companies
}

def validate_total_percentage(form, field):
    total = (form.founder1_percentage.data or 0) + \
            (form.founder2_percentage.data or 0) + \
            (form.founder3_percentage.data or 0) + \
            (form.founder4_percentage.data or 0) + \
            (form.founder5_percentage.data or 0) + \
            (form.options_pool.data or 0)
    
    if total > 100:
        raise ValidationError(f'Total equity cannot exceed 100%. Current total: {total:.1f}%')

class EquityForm(FlaskForm):
    # Initial Setup
    total_shares = FloatField('Total Shares', 
                            default=float(DEFAULT_VALUES['total_shares']),
                            validators=[NumberRange(min=1)],
                            render_kw={
                                "placeholder": "Enter total shares",
                                "type": "number",
                                "min": "1",
                                "step": "1",
                                "inputmode": "numeric"
                            })
    
    # Founder Equity
    founder1_percentage = FloatField('Founder 1 (%)', 
                                   default=DEFAULT_VALUES['founder1_percentage'],
                                   validators=[NumberRange(min=0, max=100), validate_total_percentage],
                                   render_kw={"type": "number", "min": "0", "max": "100", "step": "0.1"})
    founder2_percentage = FloatField('Founder 2 (%)', 
                                   default=DEFAULT_VALUES['founder2_percentage'],
                                   validators=[NumberRange(min=0, max=100), validate_total_percentage],
                                   render_kw={"type": "number", "min": "0", "max": "100", "step": "0.1"})
    founder3_percentage = FloatField('Founder 3 (%)', 
                                   default=DEFAULT_VALUES['founder3_percentage'],
                                   validators=[NumberRange(min=0, max=100), validate_total_percentage],
                                   render_kw={"type": "number", "min": "0", "max": "100", "step": "0.1"})
    founder4_percentage = FloatField('Founder 4 (%)', 
                                   default=DEFAULT_VALUES['founder4_percentage'],
                                   validators=[NumberRange(min=0, max=100), validate_total_percentage],
                                   render_kw={"type": "number", "min": "0", "max": "100", "step": "0.1"})
    founder5_percentage = FloatField('Founder 5 (%)', 
                                   default=DEFAULT_VALUES['founder5_percentage'],
                                   validators=[NumberRange(min=0, max=100), validate_total_percentage],
                                   render_kw={"type": "number", "min": "0", "max": "100", "step": "0.1"})
    
    # Options Pool
    options_pool = FloatField('Options Pool (%)', 
                            default=DEFAULT_VALUES['options_pool'],
                            validators=[NumberRange(min=0, max=100), validate_total_percentage],
                            render_kw={"type": "number", "min": "0", "max": "100", "step": "0.1"})
    
    # Funding Rounds
    seed_amount = FloatField('Seed Amount ($)', 
                           default=DEFAULT_VALUES['seed_amount'],
                           render_kw={"type": "number", "min": "0", "step": "1"})
    seed_valuation = FloatField('Seed Valuation ($)', 
                              default=DEFAULT_VALUES['seed_valuation'],
                              render_kw={"type": "number", "min": "0", "step": "1"})
    
    series_a_amount = FloatField('Series A Amount ($)', 
                               default=DEFAULT_VALUES['series_a_amount'],
                               render_kw={"type": "number", "min": "0", "step": "1"})
    series_a_valuation = FloatField('Series A Valuation ($)', 
                                  default=DEFAULT_VALUES['series_a_valuation'],
                                  render_kw={"type": "number", "min": "0", "step": "1"})
    
    exit_amount = FloatField('Exit Amount ($)', 
                           default=DEFAULT_VALUES['exit_amount'],
                           render_kw={"type": "number", "min": "0", "step": "1"})
    tax_type = SelectField('Tax Type', 
                         choices=[
                             ('individual', 'Individual (33%)'),
                             ('company', 'Company (23%)')
                         ], 
                         default='individual')
    
    submit = SubmitField('Calculate')

def calculate_equity(form_data):
    try:
        # Calculate initial shares for each founder
        total_shares = float(form_data['total_shares'])
        initial_shares = {
            'Founder 1': math.floor(total_shares * float(form_data['founder1_percentage']) / 100),
            'Founder 2': math.floor(total_shares * float(form_data['founder2_percentage']) / 100),
            'Founder 3': math.floor(total_shares * float(form_data['founder3_percentage']) / 100),
            'Founder 4': math.floor(total_shares * float(form_data['founder4_percentage']) / 100),
            'Founder 5': math.floor(total_shares * float(form_data['founder5_percentage']) / 100)
        }
        
        # Calculate options pool shares
        options_pool_shares = math.floor(total_shares * float(form_data['options_pool']) / 100)
        
        # Calculate shares for each round
        seed_amount = float(form_data['seed_amount'])
        seed_valuation = float(form_data['seed_valuation'])
        seed_shares = int((seed_amount / seed_valuation) * total_shares)
        total_shares_after_seed = total_shares + seed_shares
        
        series_a_amount = float(form_data['series_a_amount'])
        series_a_valuation = float(form_data['series_a_valuation'])
        series_a_shares = int((series_a_amount / series_a_valuation) * total_shares_after_seed)
        total_shares_after_rounds = total_shares_after_seed + series_a_shares

        # Calculate final ownership percentages
        final_percentages = {}
        for founder, shares in initial_shares.items():
            final_percentages[founder] = (shares / total_shares_after_rounds) * 100

        # Calculate exit amounts
        exit_amount = float(form_data['exit_amount'])
        tax_rate = TAX_RATES[form_data['tax_type']]
        exit_amounts = {}
        for founder, percentage in final_percentages.items():
            exit_amounts[founder] = (percentage / 100) * exit_amount

        # Calculate tax amounts
        tax_amounts = {}
        for founder, amount in exit_amounts.items():
            tax_amounts[founder] = amount * (tax_rate / 100)

        # Calculate net amounts
        net_amounts = {}
        for founder, amount in exit_amounts.items():
            net_amounts[founder] = amount - tax_amounts[founder]

        return {
            'initial_shares': initial_shares,
            'options_pool_shares': options_pool_shares,
            'seed_shares': seed_shares,
            'total_shares_after_seed': total_shares_after_seed,
            'series_a_shares': series_a_shares,
            'total_shares_after_rounds': total_shares_after_rounds,
            'final_percentages': final_percentages,
            'exit_amounts': exit_amounts,
            'tax_amounts': tax_amounts,
            'net_amounts': net_amounts,
            'seed_amount': seed_amount,
            'seed_valuation': seed_valuation,
            'series_a_amount': series_a_amount,
            'series_a_valuation': series_a_valuation,
            'exit_amount': exit_amount,
            'tax_rate': tax_rate
        }
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EquityForm()
    result = None
    
    if request.method == 'POST':
        try:
            # Get raw form data
            total_shares = request.form.get('total_shares', '').strip()
            if total_shares:
                # Remove commas and convert to float
                total_shares = float(total_shares.replace(',', ''))
                if total_shares < 1:
                    flash('Total shares must be at least 1', 'error')
                    return render_template('index.html', form=form, result=result)
            else:
                total_shares = DEFAULT_VALUES['total_shares']

            # Create form data dictionary
            form_data = {
                'total_shares': total_shares,
                'founder1_percentage': float(form.founder1_percentage.data),
                'founder2_percentage': float(form.founder2_percentage.data),
                'founder3_percentage': float(form.founder3_percentage.data),
                'founder4_percentage': float(form.founder4_percentage.data),
                'founder5_percentage': float(form.founder5_percentage.data),
                'options_pool': float(form.options_pool.data),
                'seed_amount': float(str(form.seed_amount.data).replace(',', '')),
                'seed_valuation': float(str(form.seed_valuation.data).replace(',', '')),
                'series_a_amount': float(str(form.series_a_amount.data).replace(',', '')),
                'series_a_valuation': float(str(form.series_a_valuation.data).replace(',', '')),
                'exit_amount': float(str(form.exit_amount.data).replace(',', '')),
                'tax_type': form.tax_type.data
            }
            
            result = calculate_equity(form_data)
            if result is None:
                flash('Error in calculation. Please check your inputs.', 'error')
        except (ValueError, TypeError) as e:
            flash(f'Error: Invalid input values. Please ensure all numeric fields contain valid numbers.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('index.html', form=form, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000) 