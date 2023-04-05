var navbarbtn = document.querySelector('.navbar-toggle')
var navbar = document.querySelector('.bg-light')
navbarbtn.addEventListener('click', ()=>{
    navbarbtn.classList.toggle('active')
    navbar.classList.toggle('active-nav')
})
