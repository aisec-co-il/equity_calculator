function formatNumber(input) {
    // For mobile devices, let the native number input handle validation
    if (input.type === 'number') {
        return;
    }
    
    // Remove any non-numeric characters
    let value = input.value.replace(/[^\d]/g, '');
    
    // Convert to number
    const numValue = parseInt(value, 10);
    
    // Validate and format
    if (!isNaN(numValue) && numValue >= 1) {
        // Format with commas
        input.value = numValue.toLocaleString();
    } else {
        input.value = '';
    }
}

function formatCurrency(input) {
    // For mobile devices, let the native number input handle validation
    if (input.type === 'number') {
        return;
    }
    
    // Remove any non-numeric characters
    let value = input.value.replace(/[^\d]/g, '');
    
    // Convert to number
    const numValue = parseInt(value, 10);
    
    // Validate and format
    if (!isNaN(numValue) && numValue >= 0) {
        // Format with commas
        input.value = numValue.toLocaleString();
    } else {
        input.value = '';
    }
}

function updatePercentage(slider, inputId) {
    const input = document.getElementById(inputId);
    input.value = slider.value;
    updateTotalPercentage();
}

function updateSlider(input) {
    const slider = input.previousElementSibling;
    slider.value = input.value;
    updateTotalPercentage();
}

function updateTotalPercentage() {
    const inputs = [
        'founder1_percentage',
        'founder2_percentage',
        'founder3_percentage',
        'founder4_percentage',
        'founder5_percentage',
        'options_pool'
    ];
    
    let total = 0;
    inputs.forEach(id => {
        const value = parseFloat(document.getElementById(id).value) || 0;
        total += value;
    });
    
    const totalElement = document.getElementById('totalPercentage');
    totalElement.textContent = total.toFixed(1);
    
    if (total > 100) {
        totalElement.parentElement.classList.add('warning');
    } else {
        totalElement.parentElement.classList.remove('warning');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('input', function() {
            dynamicCalculate();
        });
    }
});

function dynamicCalculate() {
    const form = document.querySelector('form');
    if (!form) return;
    const data = {};
    Array.from(form.elements).forEach(el => {
        if (el.name && (el.type === 'number' || el.type === 'text' || el.tagName === 'SELECT')) {
            data[el.name] = el.value;
        }
    });
    fetch('/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        if (result.error) {
            document.getElementById('dynamic-results').innerHTML = `<div class='alert alert-danger'>${result.error}</div>`;
        } else {
            document.getElementById('dynamic-results').innerHTML = renderResults(result);
        }
    });
}

function renderResults(result) {
    // You can expand this to render all result tables as needed
    let html = '';
    if (result.initial_shares) {
        html += `<h4>Initial Share Distribution</h4><table class='table'><thead><tr><th>Founder</th><th>Shares</th></tr></thead><tbody>`;
        for (const founder in result.initial_shares) {
            html += `<tr><td>${founder}</td><td>${result.initial_shares[founder].toLocaleString()}</td></tr>`;
        }
        html += `<tr><td>Options Pool</td><td>${result.options_pool_shares.toLocaleString()}</td></tr></tbody></table>`;
    }
    if (result.final_percentages) {
        html += `<h4>Final Ownership After Dilution</h4><table class='table'><thead><tr><th>Stakeholder</th><th>Percentage</th></tr></thead><tbody>`;
        for (const stakeholder in result.final_percentages) {
            html += `<tr><td>${stakeholder}</td><td>${result.final_percentages[stakeholder].toFixed(2)}%</td></tr>`;
        }
        html += `<tr class='table-info'><td><strong>Total</strong></td><td><strong>100.00%</strong></td></tr></tbody></table>`;
    }
    if (result.exit_amounts) {
        html += `<h4>Distribution of Exit Amount</h4><table class='table'><thead><tr><th>Stakeholder</th><th>Gross Amount</th><th>Tax Amount</th><th>Net Amount</th></tr></thead><tbody>`;
        for (const stakeholder in result.exit_amounts) {
            html += `<tr><td>${stakeholder}</td><td>$${result.exit_amounts[stakeholder].toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td><td>$${result.tax_amounts[stakeholder].toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td><td>$${result.net_amounts[stakeholder].toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td></tr>`;
        }
        html += `<tr class='table-info'><td><strong>Total</strong></td><td>$${result.exit_amount.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td><td>$${(result.exit_amount * result.tax_rate).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td><td>$${(result.exit_amount * (1 - result.tax_rate)).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td></tr></tbody></table>`;
    }
    return html;
} 