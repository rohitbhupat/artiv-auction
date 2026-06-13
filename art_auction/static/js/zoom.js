document.addEventListener('DOMContentLoaded', () => {
    const imageContainer = document.querySelector('.image-container');
    const targetImage = imageContainer.querySelector('.magnify');
    const viewer = document.querySelector('.viewer');
    const viewerImage = viewer.querySelector('img');
    const magnifier = document.querySelector('.magnifier');

    imageContainer.addEventListener('mousemove', (e) => {
        const rect = targetImage.getBoundingClientRect();
        const x = e.clientX - rect.left; // Mouse X position relative to the image
        const y = e.clientY - rect.top;  // Mouse Y position relative to the image

        // Calculate percentages
        const xPercent = x / rect.width;
        const yPercent = y / rect.height;

        // Set the magnifier position
        magnifier.style.left = `${x}px`;
        magnifier.style.top = `${y}px`;
        magnifier.style.display = 'block';

        // Show the viewer
        viewer.style.display = 'block';

        // Adjust the zoomed image position
        viewerImage.style.transform = `translate(-${xPercent * 100}%, -${yPercent * 100}%)`;
    });

    imageContainer.addEventListener('mouseleave', () => {
        magnifier.style.display = 'none';
        viewer.style.display = 'none';
    });
});
