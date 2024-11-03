

// const socket = io();

// document.addEventListener('DOMContentLoaded', () => {
//     document.getElementById('clear-button').addEventListener('click', async () => {
//         if (confirm('Are you sure you want to clear all images?')) {
//             try {
//                 const response = await fetch('/clear_images', { method: 'POST' });
//                 if (response.ok) {
//                     document.getElementById('imageContainer').innerHTML = '<p>No images uploaded yet.</p>';
//                     location.reload();
//                 } else {
//                     alert('Failed to clear images');
//                 }
//             } catch (error) {
//                 console.error('Error clearing images:', error);
//                 alert('Error clearing images');
//             }
//         }
//     });

//     document.getElementById('refresh-button').addEventListener('click', () => {
//         location.reload();
//     });

//     const uploadButton = document.getElementById('uploadButton');
//     const fileInput = document.getElementById('fileInput');

//     uploadButton.addEventListener('click', () => {
//         fileInput.click();
//     });

//     fileInput.addEventListener('change', (event) => {
//         const file = event.target.files[0];
//         if (file) {
//             previewAndUploadImage(file);
//         }
//     });

//     const dropZone = document.getElementById('dropZone');
//     dropZone.addEventListener('dragover', (event) => {
//         event.preventDefault();
//         dropZone.classList.add('dragover');
//     });

//     dropZone.addEventListener('dragleave', () => {
//         dropZone.classList.remove('dragover');
//     });

//     dropZone.addEventListener('drop', (event) => {
//         event.preventDefault();
//         dropZone.classList.remove('dragover');
//         const file = event.dataTransfer.files[0];
//         if (file) {
//             previewAndUploadImage(file);
//         }
//     });
// });

// socket.on('connect', () => {
//     document.querySelector('.socket-connected').style.display = 'block';
//     console.log('WebSocket connection established');
// });

// socket.on('disconnect', () => {
//     document.querySelector('.socket-connected').style.display = 'none';
// });

// socket.on('new_image', (imageUrl) => {
//     if (!document.querySelector(`img[src="${imageUrl}"]`)) {
//         const imageContainer = document.getElementById('imageContainer');
//         const newImage = document.createElement('img');
//         newImage.src = imageUrl;
//         newImage.alt = "Uploaded Image";
//         imageContainer.insertBefore(newImage, imageContainer.firstChild);
//     }
// });

// async function previewAndUploadImage(file) {
//     const formData = new FormData();
//     formData.append('image', file);

//     try {
//         const response = await fetch('/upload_image', {
//             method: 'POST',
//             body: formData
//         });

//         const result = await response.json();

//         if (response.ok) {
//             if (!document.querySelector(`img[src="${result.image_url}"]`)) {
//                 const imageContainer = document.getElementById('imageContainer');
//                 const newImage = document.createElement('img');
//                 newImage.src = result.image_url;
//                 newImage.alt = "Uploaded Image";
//                 imageContainer.insertBefore(newImage, imageContainer.firstChild);
//             }
//             socket.emit('new_image', result.image_url);
//         } else {
//             alert(result.error);
//         }
//     } catch (error) {
//         console.error('Error uploading image:', error);
//         alert('Error uploading image');
//     }
// }

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