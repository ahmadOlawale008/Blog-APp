deletebtn = document.querySelectorAll('.drop-down-delete')
forms = document.querySelectorAll('.was-validated.delete-action')
deletebtn.forEach((element, index) => {
    element.addEventListener('click', ()=>{
        forms[index].classList.toggle = 'show-delete'
    })
});

editBtnComment = document.querySelectorAll('')