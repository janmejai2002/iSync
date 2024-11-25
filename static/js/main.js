// Initialize socket
const socket = io();

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const refreshButton = document.getElementById('refresh-button');
const clearButton = document.getElementById('clear-button');
const imageContainer = document.getElementById('imageContainer');

// Socket event listeners
socket.on('connect', () => {
    document.querySelector('.socket-connected').style.display = 'block';
    console.log('WebSocket connection established');
});

socket.on('disconnect', () => {
    document.querySelector('.socket-connected').style.display = 'none';
});

socket.on('new_image', (imageUrl) => {
    console.log('Received new image:', imageUrl);
    if (!document.querySelector(`img[src="${imageUrl}"]`)) {
        const newImage = document.createElement('img');
        newImage.src = imageUrl;
        newImage.alt = "Uploaded Image";
        imageContainer.insertBefore(newImage, imageContainer.firstChild);
    }
});

socket.on('images_cleared', () => {
    imageContainer.innerHTML = '<p>No images uploaded yet.</p>';
});

// Event Listeners
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) {
        previewAndUploadImage(file);
    }
});

uploadButton.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        previewAndUploadImage(file);
    }
});

refreshButton.addEventListener('click', () => {
    location.reload();
});

clearButton.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear all images?')) {
        try {
            const response = await fetch('/clear_images', {
                method: 'POST',
            });
            
            if (response.ok) {
                imageContainer.innerHTML = '<p>No images uploaded yet.</p>';
                location.reload();
            } else {
                alert('Failed to clear images');
            }
        } catch (error) {
            console.error('Error clearing images:', error);
            alert ('Failed to clear images');
        }
    }
});

// Function to preview and upload image
function previewAndUploadImage(file) {
    const reader = new FileReader();
    reader.onload = async (e) => {
        const imageDataUrl = e.target.result;
        const imagePreview = document.createElement('img');
        imagePreview.src = imageDataUrl;
        imagePreview.alt = "Uploaded Image";
        imageContainer.insertBefore(imagePreview, imageContainer.firstChild);
        
        try {
            const response = await fetch('/upload_image', {
                method: 'POST',
                body: JSON.stringify({ imageDataUrl }),
                headers: { 'Content-Type': 'application/json' },
            });
            
            if (response.ok) {
                console.log('Image uploaded successfully');
            } else {
                alert('Failed to upload image');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('Failed to upload image');
        }
    };
    reader.readAsDataURL(file);
}

// Convert to PDF button
const convertToPdfButton = document.getElementById('convertToPdfButton');

convertToPdfButton.addEventListener('click', async () => {
    // Gather selected images
    const selectedImages = Array.from(document.querySelectorAll('.image-checkbox:checked')).map(checkbox => checkbox.value);

    if (selectedImages.length === 0) {
        alert('Please select at least one image to convert to PDF');
        return;
    }

    try {
        const response = await fetch('/convert_to_pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected_images: selectedImages })
        });

        if (response.ok) {
            // Get the generated PDF file
            const blob = await response.blob();
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = 'output.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert('Failed to generate PDF');
        }
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Failed to generate PDF');
    }
});

// "Select All" button
const selectAllButton = document.getElementById('selectAllButton');
let selectAll = true; // Track if we should select or deselect all

selectAllButton.addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.image-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll; // Set the checked state
    });
    selectAll = !selectAll; // Toggle between select and deselect
    selectAllButton.innerHTML = selectAll ? '<i class="fas fa-check-square"></i> Select All' : '<i class="fas fa-times-circle"></i> Deselect All';
});
