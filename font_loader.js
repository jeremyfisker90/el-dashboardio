// Registers display fonts at the document level so shadow-DOM cards can use them.
const l = document.createElement("link");
l.rel = "stylesheet";
l.href = "https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Cinzel:wght@700;800&display=swap";
document.head.appendChild(l);
