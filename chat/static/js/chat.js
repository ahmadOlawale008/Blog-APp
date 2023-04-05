const room_name = JSON.parse(document.querySelector('#room_name').textContent)
const room_id = JSON.parse(document.querySelector('#room_id').textContent)
const other_user_image = JSON.parse(document.querySelector('#other_user_image').textContent)
const user_image = JSON.parse(document.querySelector('#user_image').textContent)

const messageForm = document.querySelector('.send-message-form')
const inputMessageForm = document.querySelector('.input-message-form')
const username = JSON.parse(document.querySelector('#username').textContent)
const chatBox = document.querySelector('.chat-wrap-content')
inputMessageForm.focus()
const url = `ws://${window.location.host}/ws/chat/${room_id}/`
const socket = new ReconnectingWebSocket(url)
const chat = document.querySelectorAll('.content-dis')
socket.onmessage = function(e){
    const data = JSON.parse(e.data) 
    checkData(data)
    console.log( "This is data: ",data)
}
socket.onclose = function(e){
    console.error('Socket is closed!')
}

socket.onopen = function(e){
    socket.send(JSON.stringify({'to': room_name, 'author': username, 'action': 'get_message'}))
}
function checkData(data){
    if(data.command == 'get_message'){
        const message_arr = data.message

        for (let i = 0; i < message_arr.length; i++) {
            if(message_arr[i].author == username){
                chatBox.innerHTML +=`
                <div class="chat-flex-page my-2 sender-flex">
                <div class="sender-pov">
                    <span><img class="rounded-circle mx-auto img-displayed-chat rounded-circle-small" src="${user_image}" alt="${username} image"></span>
                </div>
                <div class="sender-message-box d-flex flex-column">
                    <span class="fs-7 my-0 fw-bold">You</span>
                    <span class="fs-6">${message_arr[i].description}</span>
                    <small class='date-parsed fg-light'></small>
                    <span  id='date-time-ago' class='display-none fg-light' >${message_arr[i].date_created}</span>
                    
                </div>
            </div>`
            }if(message_arr[i].author != username){
            chatBox.innerHTML+= `
            <div class="chat-flex-page my-2 receiver-flex">
                <div class="receiver-pov">
                    <span><img class="rounded-circle img-displayed-chat mx-auto rounded-circle-small" src="${other_user_image}" alt="${room_name} image"></span>
                </div>
                <div class="receiver-message-box d-flex flex-column">
                    <span class="fs-7 my-0 fw-bold">${message_arr[i].author}</span>
                    <span class="fs-6">${message_arr[i].description}</span>
                    <small class='date-parsed'></small>
                    <span id='date-time-ago' class='display-none fg-dark'>${message_arr[i].date_created}</span>
                </div>
            </div>`

        }}}
    if(data.command=='create_message'){
        console.log(data)
        const message_arr = data.message
            if(message_arr.author == username){
                chatBox.innerHTML +=`
                <div class="chat-flex-page my-2 sender-flex">
                <div class="sender-pov">
                    <span><img class="rounded-circle mx-auto img-displayed-chat rounded-circle-small" src="${user_image}" alt="${username} image"></span>
                </div>
                <div class="sender-message-box d-flex flex-column">
                    <span class="fs-7 my-0 fw-bold">You</span>
                    <span class="fs-6">${message_arr.description}</span>
                    <small class='date-parsed fg-light'></small>
                    <span  id='date-time-ago' class='display-none fg-light' >${message_arr.date_created}</span>
                </div>
            </div>`
            }if(message_arr.author != username){  
            chatBox.innerHTML+= `
            <div class="chat-flex-page my-2 receiver-flex">
                <div class="receiver-pov">
                    <span><img class="rounded-circle mx-auto img-displayed-chat rounded-circle-small" src="${other_user_image}" alt="${room_name} image"></span>
                </div>
                <div class="receiver-message-box d-flex flex-column">
                    <span class="fs-7 my-0 fw-bold">${message_arr.author}</span>
                    <span class="fs-6">${String(message_arr.description)}</span>
                    <small class='date-parsed'></small>
                    <span  id='date-time-ago' class='display-none fg-light' >${message_arr.date_created}</span>
                </div>
            </div>`
}   
 
}
const dateTimeDatas = document.querySelectorAll('#date-time-ago')
const dateparsed = document.querySelectorAll('.date-parsed')
dateTimeDatas.forEach((item, index)=>{
    setInterval(function(){
        const date = convertDate(item.innerHTML)
        dateparsed[index].innerHTML = date
    }, 1000)
})

}

function convertDate(val){
    const presentDate = new Date()
    const date = new Date(val)
    const Datemilliseconds = date.getTime()
    const presentDateMilliseconds = presentDate.getTime()
    const intervals = (presentDateMilliseconds - Datemilliseconds)
    const intervalSecs = intervals / 1000    
    const days = Math.floor(intervalSecs / 3600 / 24)
    const years = Math.floor(intervalSecs / 31557600)
    const weeks = Math.floor(intervalSecs / 3600 / 24 / 7) 
    if (weeks > 1){
        return `${weeks} weeks ago`
    }
    if(years ==1){
        return `${years} year`
    }else if(years > 1){
        return `${years} years`}

    const hours = Math.floor(intervalSecs / 3600) % 24
    const mins = Math.floor(intervalSecs / 60 )% 60
    const secs = Math.floor(intervalSecs) % 60
    return `${days == 1 ? days+'day' : days==0 ? '': days +' days'} 
    ${hours == 1 ? hours+' hr' : hours==0 ? '': hours +' hrs'} 
    ${mins == 1 ? mins+' min' : mins==0 ? '0 min': mins +' mins'} ago`
}
messageForm.addEventListener('submit', (e)=>{
    e.preventDefault()
    socket.send(JSON.stringify({'description': inputMessageForm.value, 'to': room_name, 'author': username, 'action': 'create_message'}))
    inputMessageForm.value = ''
})
