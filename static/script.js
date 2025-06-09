function formatNumber(input) {
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