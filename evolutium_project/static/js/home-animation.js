document.addEventListener('DOMContentLoaded', function() {
    const glassPane = document.getElementById('glass-pane');
    const backgroundCycler = document.getElementById('background-cycler');
    const staticShardsContainer = document.getElementById('static-shards');
    const mainContent = document.querySelector('.home-hero');

    if (!glassPane || !backgroundCycler || !mainContent) return;
    const shatterPieceCount = 40;
    const backgroundImages = [
        "https://images.unsplash.com/photo-1639322537228-f710d846310a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8Y3J5cHRvfHx8fHx8MTY4Mzk0NTI1MQ&ixlib=rb-4.0.3&q=80&w=1080"
    ];
    let currentImageIndex = 0;

    function createShatter() {
        for (let i = 0; i < shatterPieceCount; i++) {
            const piece = document.createElement('div');
            piece.classList.add('glass-piece');
            piece.style.top = '50%';
            piece.style.left = '50%';
            const rotation = Math.random() * 720 - 360;
            const translateX = (Math.random() - 0.5) * window.innerWidth * 2;
            const translateY = (Math.random() - 0.5) * window.innerHeight * 2;
            const scale = Math.random() * 1.5 + 0.5;

            piece.style.setProperty('--end-rotation', `${rotation}deg`);
            piece.style.setProperty('--end-translate-x', `${translateX}px`);
            piece.style.setProperty('--end-translate-y', `${translateY}px`);
            piece.style.setProperty('--end-scale', scale);

            glassPane.appendChild(piece);
        }
    }

    function startBackgroundCycle() {
        setInterval(() => {
            currentImageIndex = (currentImageIndex + 1) % backgroundImages.length;
            const newImg = new Image();
            newImg.src = backgroundImages[currentImageIndex];
            newImg.onload = () => {
                backgroundCycler.style.backgroundImage = `url(${newImg.src})`;
            };
        }, 5000);
    }

    createShatter();
    backgroundCycler.style.backgroundImage = `url(${backgroundImages[0]})`;

    setTimeout(() => {
        document.body.classList.add('animation-started');
        startBackgroundCycle();
    }, 1000);
    setTimeout(() => {
        if(glassPane) glassPane.remove();
    }, 3000);

});