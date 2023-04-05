const usernamefield = document.querySelector('.username_field')
const usernamefieldback = document.querySelector('.username_feed-back')
const emailField = document.querySelector('.email_field')
const email_field_back = document.querySelector('.email-feed-back')
const passwordField = document.querySelector('.password_field')
const passwordFieldBack = document.querySelector('.password-feed-back')
const confirmPassword = document.querySelector('.confirm_password_field')
const confirmPasswordFieldBack = document.querySelector('.confirm_password-feed-back')
const showBtn = document.querySelector('.show-btn-password')
const submitBtn = document.querySelector('.submit-btn')
const prependImage = document.querySelector(".input-image-prepend")
usernamefield.focus()
usernamefield.addEventListener('keyup', usernameValidation)
function usernameValidation(e){
    const username_field_value = e.target.value
    if(username_field_value.length > 0){
        fetch('/register/validate_username/', {
            body: JSON.stringify({username: username_field_value}),
            method: 'POST'
        }).then((res)=>res.json()).then(data=>{
            if(data.error){
                usernamefield.classList.add('is-invalid')
                usernamefield.classList.remove('is-valid')
                usernamefieldback.innerHTML = data.error
                usernamefieldback.style.display = 'block!Important'
                submitBtn.disabled = true
                return false
            }else{
                usernamefieldback.innerHTML = ''
                usernamefield.classList.remove('is-invalid')
                usernamefield.classList.add('is-valid')
                submitBtn.removeAttribute('disabled')
                return true
            }
        })
    }
}
emailField.addEventListener('keyup', emailValidation)
function emailValidation(e){
    const emailValue = e.target.value
    if(emailValue.length > 0){
        fetch('/register/validate_email/', {
            body: JSON.stringify({email: emailValue}),
            method: 'POST'
        }).then((res)=>res.json()).then(data=>{
            if(data.error){
                emailField.classList.add('is-invalid')
                emailField.classList.remove('is-valid')
                submitBtn.disabled = true
                email_field_back.innerHTML = data.error
                email_field_back.style.display = 'block!Important'
                console.log(data.error)

            }else{
                submitBtn.removeAttribute('disabled')
                email_field_back.innerHTML = ''
                emailField.classList.remove('is-invalid')
                emailField.classList.add('is-valid')
            }
        })
    }
}
passwordField.addEventListener('keyup', passwordValidation)
function passwordValidation(e){
    const passwordValue = e.target.value
    if(passwordValue.length > 0){
        fetch('/register/validate_password/', {
            body: JSON.stringify({password: passwordValue}),
            method: 'POST'
        }).then((res)=>res.json()).then(data=>{
            if(data.error){
                passwordField.classList.add('is-invalid')
                passwordField.classList.remove('is-valid')
                passwordFieldBack.innerHTML = data.error
                passwordFieldBack.style.display = 'block!Important'
                submitBtn.disabled = true

            }else{
                passwordFieldBack.style.display = 'none!Important'
                passwordFieldBack.innerHTML = ''
                passwordField.classList.remove('is-invalid')
                passwordField.classList.add('is-valid')
                submitBtn.removeAttribute('disabled')
            }
        })
    }
}
confirmPassword.addEventListener('keyup', confirmPasswordValidation)
function confirmPasswordValidation(e){
    const confirmPasswordValue = e.target.value
    const passwordValue = passwordField.value
    if(confirmPasswordValue.length > 0){
        fetch('/register/validate_confirmPassword/', {
            body: JSON.stringify({password: passwordValue, confirmPassword: confirmPasswordValue}),
            method: 'POST'
        }).then((res)=>res.json()).then(data=>{
            if(data.error){
                confirmPassword.classList.add('is-invalid')
                confirmPassword.classList.remove('is-valid')
                confirmPasswordFieldBack.innerHTML = data.error
                submitBtn.disabled = true
                confirmPasswordFieldBack.style.display = 'block!Important'

            }else{
                confirmPasswordFieldBack.style.display = 'none!Important'
                confirmPasswordFieldBack.innerHTML = ''
                confirmPassword.classList.remove('is-invalid')
                confirmPassword.classList.add('is-valid')
                submitBtn.removeAttribute('disabled')

            }
        })
    }
}
showBtn.addEventListener('click', ()=>{
    if(showBtn.classList.contains('show-password')){
        showBtn.classList.add('hide-password')
        showBtn.classList.remove('show-password')
        passwordField.setAttribute('type', 'text')
        confirmPassword.setAttribute('type', 'text')
        prependImage.innerHTML = 'visibility_off'

    }else{
        showBtn.classList.remove('hide-password')
        showBtn.classList.add("show-password")
        passwordField.setAttribute('type', 'password')
        confirmPassword.setAttribute('type', 'password')
        prependImage.innerHTML = 'visibility'


    }
})