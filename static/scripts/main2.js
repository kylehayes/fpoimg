document.addEventListener('DOMContentLoaded', function() {
    const widthInput = document.getElementById('width');
    const heightInput = document.getElementById('height');
    const captionInput = document.getElementById('caption');
    const bgColorInput = document.getElementById('bg-color');
    const textColorInput = document.getElementById('text-color');
    const generateBtn = document.getElementById('generate-btn');
    const previewImage = document.getElementById('preview-image');
    const urlDisplay = document.getElementById('url-display');
    const copyBtn = document.getElementById('copy-btn');
    const previewFrame = document.querySelector('.preview-frame');
    
    // Initialize with default values
    updatePreview();
    
    generateBtn.addEventListener('click', updatePreview);
    
    copyBtn.addEventListener('click', function() {
        const urlText = urlDisplay.textContent.trim();
        navigator.clipboard.writeText(urlText).then(function() {
            copyBtn.textContent = 'Copied!';
            setTimeout(function() {
                copyBtn.textContent = 'Copy';
            }, 2000);
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
        });
    });
    
    function updatePreview() {
        const width = widthInput.value || 400;
        const height = heightInput.value || 350;
        const bgColor = bgColorInput.value.replace('#', '') || 'e6e6e6';
        const textColor = textColorInput.value.replace('#', '') || '8F8F8F';
        const caption = captionInput.value || 'Preview';
        
        let previewWidth, previewHeight;
       
        previewWidth = width;
        previewHeight = height;
        
        previewFrame.style.width = `${previewWidth}px`;
        previewFrame.style.height = `${previewHeight}px`;
        
        const url = `https://fpoimg.com/${width}x${height}?text=${caption}&bg_color=${bgColor}&text_color=${textColor}`;
        previewImage.src = url;
        
        // Update URL display
<<<<<<< HEAD
        urlDisplay.textContent = url;
=======
        urlDisplay.innerHTML = `${url}`;
>>>>>>> 869d360 (feat: new look)
    }
    
    // Make the sizing inputs update on change
    [widthInput, heightInput, captionInput, bgColorInput, textColorInput].forEach(input => {
        input.addEventListener('input', function() {
            // Debounce for performance
            clearTimeout(input.timeout);
            input.timeout = setTimeout(updatePreview, 300);
        });
    });
});