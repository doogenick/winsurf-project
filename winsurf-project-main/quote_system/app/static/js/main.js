// Margin slider functionality
function setupMarginSlider() {
    const slider = document.getElementById('margin-slider');
    const value = document.getElementById('margin-value');
    
    if (slider && value) {
        slider.addEventListener('input', function() {
            value.textContent = this.value + '%';
            updateQuotePreview();
        });
    }
}

// Dynamic activity form
function addActivityForm() {
    const activityCount = document.getElementById('activity-count').value;
    const activityContainer = document.getElementById('activity-container');
    
    const newActivity = document.createElement('div');
    newActivity.className = 'activity-card mb-3';
    newActivity.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <input type="text" class="form-control" name="activity_name_${activityCount}" placeholder="Activity Name">
            </div>
            <div class="col-md-4">
                <input type="number" class="form-control" name="activity_cost_${activityCount}" placeholder="Cost">
            </div>
            <div class="col-md-3">
                <input type="number" class="form-control" name="activity_duration_${activityCount}" placeholder="Duration (hours)">
            </div>
            <div class="col-md-1">
                <button type="button" class="btn btn-danger btn-sm remove-activity" onclick="removeActivity(this)">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        </div>
    `;
    
    activityContainer.appendChild(newActivity);
    document.getElementById('activity-count').value = parseInt(activityCount) + 1;
}

function removeActivity(button) {
    button.closest('.activity-card').remove();
}

// Quote preview update
function updateQuotePreview() {
    const formData = new FormData(document.getElementById('quote-form'));
    fetch('/api/preview-quote', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('quote-preview').innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Quote Preview</h5>
                    <p><strong>Total Cost:</strong> $${data.total_cost.toFixed(2)}</p>
                    <p><strong>Margin:</strong> ${data.margin_percentage}%</p>
                    <p><strong>Final Price:</strong> $${data.final_price.toFixed(2)}</p>
                </div>
            </div>
        `;
    })
    .catch(error => console.error('Error:', error));
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupMarginSlider();
});
