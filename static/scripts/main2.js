document.addEventListener('DOMContentLoaded', function() {
    const widthInput = document.getElementById('width');
    const heightInput = document.getElementById('height');
    const captionInput = document.getElementById('caption');
    const bgColorInput = document.getElementById('bg-color');
    const textColorInput = document.getElementById('text-color');
    const gradientSelect = document.getElementById('gradient');
    const customGradientControls = document.getElementById('custom-gradient-controls');
    const gradientColor1 = document.getElementById('gradient-color1');
    const gradientColor2 = document.getElementById('gradient-color2');
    const gradientAngle = document.getElementById('gradient-angle');
    const generateBtn = document.getElementById('generate-btn');
    const previewImage = document.getElementById('preview-image');
    const urlDisplay = document.getElementById('url-display');
    const copyBtn = document.getElementById('copy-btn');
    const previewFrame = document.querySelector('.preview-frame');

    // Hamburger menu functionality
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mainNav = document.getElementById('main-nav');

    // Create menu overlay
    const menuOverlay = document.createElement('div');
    menuOverlay.className = 'menu-overlay';
    document.body.appendChild(menuOverlay);
    
    function toggleMenu() {
        hamburgerBtn.classList.toggle('active');
        mainNav.classList.toggle('active');
        menuOverlay.classList.toggle('active');
        
        const isExpanded = hamburgerBtn.classList.contains('active');
        hamburgerBtn.setAttribute('aria-expanded', isExpanded);
        
        if (isExpanded) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
    
    hamburgerBtn.addEventListener('click', toggleMenu);
    menuOverlay.addEventListener('click', toggleMenu);
    
    const menuItems = mainNav.querySelectorAll('a');
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                toggleMenu();
            }
        });
    });
    
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && mainNav.classList.contains('active')) {
            hamburgerBtn.classList.remove('active');
            mainNav.classList.remove('active');
            menuOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Color picker sync — pairs each color picker with its text input
    function syncColorPair(pickerId, textId) {
        const picker = document.getElementById(pickerId);
        const text = document.getElementById(textId);
        if (!picker || !text) return;

        picker.addEventListener('input', function() {
            text.value = this.value;
            text.dispatchEvent(new Event('input'));
        });
        text.addEventListener('input', function() {
            // Only update picker if it's a valid 6-digit hex
            const val = this.value.replace('#', '');
            if (/^[0-9A-Fa-f]{6}$/.test(val)) {
                picker.value = '#' + val;
            }
        });
    }

    syncColorPair('bg-color-picker', 'bg-color');
    syncColorPair('text-color-picker', 'text-color');
    syncColorPair('gradient-color1-picker', 'gradient-color1');
    syncColorPair('gradient-color2-picker', 'gradient-color2');

    // Preset default angles (matching server-side PRESETS)
    const presetAngles = {
        sunset: 135, ocean: 180, forest: 135, lavender: 135, midnight: 180,
        fire: 135, sky: 180, peach: 135, mint: 135, berry: 135,
        coral: 135, steel: 180, candy: 135, arctic: 135, ember: 180,
        twilight: 180, spring: 135, neon: 135, rose: 135, shadow: 180
    };

    // Track if user manually changed the angle
    gradientAngle.dataset.userChanged = 'false';
    gradientAngle.addEventListener('input', function() {
        gradientAngle.dataset.userChanged = 'true';
    });

    // Show/hide custom gradient inputs and update angle to preset default
    gradientSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customGradientControls.style.display = 'block';
        } else {
            customGradientControls.style.display = 'none';
        }
        // Update angle field to preset default
        if (this.value in presetAngles) {
            gradientAngle.value = presetAngles[this.value];
            gradientAngle.dataset.userChanged = 'false';
        }
        updatePreview();
    });

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
        const gradient = gradientSelect.value;
        const angle = gradientAngle.value || '135';
        
        previewFrame.style.width = `${width}px`;
        previewFrame.style.height = `${height}px`;
        
        let params = [`text=${encodeURIComponent(caption)}`, `text_color=${textColor}`];

        if (gradient && gradient !== '') {
            if (gradient === 'custom') {
                const c1 = gradientColor1.value.replace('#', '') || 'FF5E3A';
                const c2 = gradientColor2.value.replace('#', '') || 'FF9F40';
                params.push(`gradient=${c1},${c2}`);
                params.push(`gradient_angle=${angle}`);
            } else {
                params.push(`gradient=${gradient}`);
                // Only send angle if user changed it from the preset default
                if (gradientAngle.dataset.userChanged === 'true') {
                    params.push(`gradient_angle=${angle}`);
                }
            }
        } else {
            params.push(`bg_color=${bgColor}`);
        }

        const queryString = params.join('&');
        const url = `https://fpoimg.com/${width}x${height}?${queryString}`;
        // Use relative URL for preview so it works locally and in production
        previewImage.src = `/${width}x${height}?${queryString}`;
        urlDisplay.innerHTML = url;
    }
    
    // Make all inputs update on change
    hideDimsInput.addEventListener('change', updatePreview);

    [widthInput, heightInput, captionInput, bgColorInput, textColorInput,
     gradientColor1, gradientColor2, gradientAngle].forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(input.timeout);
            input.timeout = setTimeout(updatePreview, 300);
        });
    });
});

        });
    });
});
