const burger_menu = document.querySelector("#burger");
const menu_elements = document.querySelectorAll("#menu>ul>li");
const submenu_elements = document.querySelectorAll("#menu > ul > li > ul > li");

burger_menu.addEventListener("click", () => {
  // Ajouter a burger_menu la classe active pour qu'il s'anime
  burger_menu.classList.toggle("active");
  // Afficher le menu
  document.querySelector("#menu").classList.toggle("active");
});

menu_elements.forEach((elt) => {
  elt.addEventListener("click", () => {
    // Afficher le sous-menu
    elt.classList.toggle("active");
  });
});

submenu_elements.forEach((elt) => {
  elt.addEventListener("click", () => {
    // Si un élément du sous-menu cliqué,
    // fermer le menu
    burger_menu.classList.toggle("active");
    document.querySelector("#menu").classList.toggle("active");
  });
});

// Fonction pour afficher le pop-up pendant 3 secondes
function showPopup(message) {
    var popup = document.getElementById("popup");
    popup.innerHTML = message;
    popup.style.display = "block";
    setTimeout(function() {
        popup.style.display = "none";
    }, 2000); // Affiche le pop-up pendant 3 secondes
}