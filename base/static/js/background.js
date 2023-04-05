var btn = document.querySelector('.toggle-modeBtn')
var body = document.querySelector('body')
var ref = document.querySelector('.backg-mode')
var isDark = localStorage.getItem('theme')

if (isDark == null){
    ref.setAttribute('href', light_mode)

}
if (isDark != null){
    if(isDark == 'true'){
        ref.setAttribute('href', dark_mode)
        body.classList.toggle('dark-mode')
        body.classList.remove('light-mode')
        btn.innerHTML =  `   <span style="color: #fff!important;" class="mx-3 cursor-pointer material-symbols-outlined filled-icon fw-lighter">
                                light_mode 
                                </span>`
    }else{
        ref.setAttribute('href', light_mode)
        body.classList.toggle('light-mode')
        body.classList.remove('dark-mode')
        if (pg=='chat_pg'){
            btn.innerHTML =  `<span style="color: #000!important;" class="mx-3 cursor-pointer material-symbols-outlined filled-icon fw-lighter">
            dark_mode 
        </span>`   
        }else{
            btn.innerHTML =  `<span style="color: #fff!important;" class="mx-3 cursor-pointer material-symbols-outlined filled-icon fw-lighter">
            dark_mode 
        </span>`
        }
    }
}


btn.addEventListener('click', ()=>{
    var curbody = body.classList.contains('dark-mode') ? true : false
    localStorage.setItem('theme', curbody)
    if(Boolean(curbody)){
    ref.setAttribute('href', light_mode)
    body.classList.toggle('light-mode')
    body.classList.remove('dark-mode')
    localStorage.setItem('theme', false)
    if (pg=='chat_pg'){
        btn.innerHTML =  `<span style="color: #000!important;" class="mx-3 cursor-pointer material-symbols-outlined filled-icon fw-lighter">
        dark_mode 
    </span>`   
    }else{
        btn.innerHTML =  `   <span style="color: #fff!important;" class="mx-3 cursor-pointer material-symbols-outlined filled-icon fw-lighter">
        dark_mode 
     </span>`
    }

    }else{
    ref.setAttribute('href', dark_mode)
    body.classList.toggle('dark-mode')
    body.classList.remove('light-mode')
    localStorage.setItem('theme', true)
    btn.innerHTML =  `   <span style="color: #fff!important;" class="mx-3 cursor-pointer material-symbols-outlined filled-icon fw-lighter">
                               light_mode 
                            </span>`
    }
})