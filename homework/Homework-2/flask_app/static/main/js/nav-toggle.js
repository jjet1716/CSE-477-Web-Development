/* toggles mobile nav bar on click */

const hamburger = document.querySelector('.nav-hamburger');
const nav_menu = document.getElementsByClassName('nav');
const page_content = document.getElementById('main');

hamburger.addEventListener('click', () => {
    nav_menu[0].classList.toggle('open');
    page_content.classList.toggle('open');
});