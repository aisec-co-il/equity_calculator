from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, ValidationError
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Default values for the calculator
DEFAULT_VALUES = {
    'total_shares': 10000000,  # 10 million shares
    'founder1_percentage': 20.0,
    'founder2_percentage': 20.0,
    'founder3_percentage': 20.0,
    'founder4_percentage': 20.0,
    'founder5_percentage': 20.0,
    'options_pool': 10.0,
    'seed_amount': 1000000,  # $1M
    'seed_valuation': 5000000,  # $5M
    'series_a_amount': 5000000,  # $5M
    'series_a_valuation': 20000000,  # $20M
    'exit_amount': 100000000  # $100M
}

# Tax rates for Israel
TAX_RATES = {
    'individual': 0.25,  # 25% for individuals
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
    total_shares = FloatField('Total Shares', default=DEFAULT_VALUES['total_shares'])
    
    # Founder Equity
    founder1_percentage = FloatField('Founder 1 (%)', default=DEFAULT_VALUES['founder1_percentage'], validators=[NumberRange(min=0, max=100), validate_total_percentage])
    founder2_percentage = FloatField('Founder 2 (%)', default=DEFAULT_VALUES['founder2_percentage'], validators=[NumberRange(min=0, max=100), validate_total_percentage])
    founder3_percentage = FloatField('Founder 3 (%)', default=DEFAULT_VALUES['founder3_percentage'], validators=[NumberRange(min=0, max=100), validate_total_percentage])
    founder4_percentage = FloatField('Founder 4 (%)', default=DEFAULT_VALUES['founder4_percentage'], validators=[NumberRange(min=0, max=100), validate_total_percentage])
    founder5_percentage = FloatField('Founder 5 (%)', default=DEFAULT_VALUES['founder5_percentage'], validators=[NumberRange(min=0, max=100), validate_total_percentage])
    
    # Options Pool
    options_pool = FloatField('Options Pool (%)', default=DEFAULT_VALUES['options_pool'], validators=[NumberRange(min=0, max=100), validate_total_percentage])
    
    # Funding Rounds
    seed_amount = FloatField('Seed Amount ($)', default=DEFAULT_VALUES['seed_amount'])
    seed_valuation = FloatField('Seed Valuation ($)', default=DEFAULT_VALUES['seed_valuation'])
    
    series_a_amount = FloatField('Series A Amount ($)', default=DEFAULT_VALUES['series_a_amount'])
    series_a_valuation = FloatField('Series A Valuation ($)', default=DEFAULT_VALUES['series_a_valuation'])
    
    exit_amount = FloatField('Exit Amount ($)', default=DEFAULT_VALUES['exit_amount'])
    tax_type = SelectField('Tax Type', choices=[
        ('individual', 'Individual (25%)'),
        ('company', 'Company (23%)')
    ], default='individual')
    
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
        
        # Calculate ownership after each round
        current_shares = total_shares
        ownership = {
            'Founder 1': float(form_data['founder1_percentage']),
            'Founder 2': float(form_data['founder2_percentage']),
            'Founder 3': float(form_data['founder3_percentage']),
            'Founder 4': float(form_data['founder4_percentage']),
            'Founder 5': float(form_data['founder5_percentage']),
            'Options Pool': float(form_data['options_pool'])
        }
        
        # Seed Round
        seed_shares = math.floor(float(form_data['seed_amount']) * current_shares / float(form_data['seed_valuation']))
        current_shares += seed_shares
        ownership = {k: (v * total_shares / current_shares) for k, v in ownership.items()}
        ownership['Seed Investors'] = (seed_shares / current_shares) * 100
        
        # Series A
        series_a_shares = math.floor(float(form_data['series_a_amount']) * current_shares / float(form_data['series_a_valuation']))
        current_shares += series_a_shares
        ownership = {k: (v * (current_shares - series_a_shares) / current_shares) for k, v in ownership.items()}
        ownership['Series A Investors'] = (series_a_shares / current_shares) * 100
        
        # Calculate exit proceeds
        tax_rate = TAX_RATES[form_data['tax_type']]
        exit_proceeds = {}
        
        # Calculate proceeds for all stakeholders
        for stakeholder, percentage in ownership.items():
            gross_amount = float(form_data['exit_amount']) * (percentage / 100)
            tax_amount = gross_amount * tax_rate
            net_amount = gross_amount - tax_amount
            exit_proceeds[stakeholder] = {
                'gross_amount': gross_amount,
                'tax_amount': tax_amount,
                'net_amount': net_amount
            }
        
        return {
            'initial_shares': initial_shares,
            'options_pool_shares': options_pool_shares,
            'final_ownership': ownership,
            'total_shares_after_rounds': current_shares,
            'exit_proceeds': exit_proceeds,
            'tax_rate': tax_rate * 100,
            'exit_amount': float(form_data['exit_amount'])
        }
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EquityForm()
    result = None
    
    if form.validate_on_submit():
        try:
            form_data = {
                'total_shares': form.total_shares.data,
                'founder1_percentage': form.founder1_percentage.data,
                'founder2_percentage': form.founder2_percentage.data,
                'founder3_percentage': form.founder3_percentage.data,
                'founder4_percentage': form.founder4_percentage.data,
                'founder5_percentage': form.founder5_percentage.data,
                'options_pool': form.options_pool.data,
                'seed_amount': form.seed_amount.data,
                'seed_valuation': form.seed_valuation.data,
                'series_a_amount': form.series_a_amount.data,
                'series_a_valuation': form.series_a_valuation.data,
                'exit_amount': form.exit_amount.data,
                'tax_type': form.tax_type.data
            }
            
            result = calculate_equity(form_data)
            if result is None:
                flash('Error in calculation. Please check your inputs.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('index.html', form=form, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=4000) 