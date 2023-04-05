const selected_tag = document.querySelector('.selecttagsoa')
var text_ar = document.querySelector('.textarea-dispa09')
var tags = document.querySelector('.tags-a09ka')
var spinner = document.querySelector('.spinner-border')
getItem()

async function getItem(){
    try {
        let response = await fetch('/json/', {
            method: 'get',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
        })
        setTimeout(async () => {
            spinner.classList.add('not-visible')
            if(response.status == 200){
                try {
                var data = await response.json()
                    await data.forEach(element => {
                        selected_tag.innerHTML += `<option value='${element.user_followed}'><a href="/profile/${element.user_followed}">${element.user_followed}</a></option>`
                    });
                    selected_tag.addEventListener('change', ()=>{
                        selected_value = selected_tag.options[selected_tag.selectedIndex].value
                        text_ar.value += selected_value
                    })
                }catch(error) {
                    setTimeout(async()=> {
                        tags.innerHTML = '<span class="alert alert-danger">Error fetching followers, please try logging in !!!</span>'
                        }, 1000);
                }

            }else{
                spinner.classList.remove('not-visible')
            }
           
        }, 2000);

    } catch(error) {
        setTimeout(async() => {
        tags.innerHTML = 'Error fetching followers, please try logging in'
        }, 2000);
        throw new TypeError(error.message)
    }
}

// GET THE CHOOSEN ITEM
// DISPLAY TAGS WHEN @ IS PRESSED
text_ar.addEventListener('keyup', ()=>{
        var textval = text_ar.value
        if(textval[textval.length-1] == '@'){
            tags.classList.add('active')
        }
})
text_ar.addEventListener('keydown', ()=>{
    tags.classList.remove('active')
})
