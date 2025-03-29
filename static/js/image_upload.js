// image_upload.js - Handles image upload and analysis functionality

document.addEventListener('DOMContentLoaded', function() {
    // Setup the file input change event
    setupFileInputPreview();
    
    // Setup the form submission
    setupAnalysisForm();
});

function setupFileInputPreview() {
    const fileInput = document.getElementById('image-upload');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImage = document.getElementById('image-preview');
    
    if (!fileInput || !previewContainer || !previewImage) return;
    
    fileInput.addEventListener('change', function() {
        // Clear previous preview
        previewImage.src = '';
        previewContainer.classList.add('d-none');
        
        // Check if a file is selected
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check file type
            if (!file.type.match('image.*')) {
                alert('Please select an image file (JPG, JPEG, or PNG).');
                fileInput.value = '';
                return;
            }
            
            // Check file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size exceeds 5MB. Please select a smaller image.');
                fileInput.value = '';
                return;
            }
            
            // Create a FileReader to read the image
            const reader = new FileReader();
            
            // Setup the FileReader onload event
            reader.onload = function(e) {
                // Set the preview image source
                previewImage.src = e.target.result;
                previewContainer.classList.remove('d-none');
                
                // Enable the analyze button
                const analyzeButton = document.getElementById('analyze-button');
                if (analyzeButton) {
                    analyzeButton.disabled = false;
                }
            };
            
            // Read the image as a data URL
            reader.readAsDataURL(file);
        }
    });
}

function setupAnalysisForm() {
    const analysisForm = document.getElementById('analysis-form');
    
    if (!analysisForm) return;
    
    analysisForm.addEventListener('submit', function(e) {
        // Don't need to prevent default as we want the form to submit normally for server-side processing
        
        // Show loading indicator
        const loadingIndicator = document.getElementById('analysis-loading');
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
        }
        
        // Disable the submit button to prevent multiple submissions
        const submitButton = document.getElementById('analyze-button');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        }
    });
}

// Function to display analysis results in a modal
function showAnalysisModal(result) {
    // This function would be called after receiving AJAX results, but since we're using
    // server-side rendering for this feature, it's not needed in the current implementation.
    // Kept here for future AJAX implementation possibility.
    
    const modalTitle = document.getElementById('analysisModalLabel');
    const modalBody = document.getElementById('analysisModalBody');
    
    if (!modalTitle || !modalBody) return;
    
    // Set modal title
    modalTitle.textContent = 'Image Analysis Results';
    
    // Set modal body content
    modalBody.innerHTML = `
        <div class="alert ${result.confidence > 0.7 ? 'alert-success' : 'alert-warning'}">
            <h5>Detected: ${result.disaster_type}</h5>
            <p>Confidence: ${Math.round(result.confidence * 100)}%</p>
        </div>
        <p>${result.description}</p>
    `;
    
    // Show the modal
    const analysisModal = new bootstrap.Modal(document.getElementById('analysisModal'));
    analysisModal.show();
}

// Function to clear the form
function clearImageUpload() {
    const fileInput = document.getElementById('image-upload');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImage = document.getElementById('image-preview');
    const locationInput = document.getElementById('upload-location');
    
    if (fileInput) fileInput.value = '';
    if (previewContainer) previewContainer.classList.add('d-none');
    if (previewImage) previewImage.src = '';
    if (locationInput) locationInput.value = '';
    
    // Disable the analyze button
    const analyzeButton = document.getElementById('analyze-button');
    if (analyzeButton) {
        analyzeButton.disabled = true;
    }
}

// Function to handle recent analysis clicks
function viewRecentAnalysis(id) {
    // Fetch the analysis details
    fetch(`/api/image-analysis/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Analysis fetch failed');
            }
            return response.json();
        })
        .then(data => {
            showAnalysisModal(data);
        })
        .catch(error => {
            console.error('Error fetching analysis details:', error);
            alert('Failed to load analysis details. Please try again.');
        });
}
