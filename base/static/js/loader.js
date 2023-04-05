var pageLoader = document.getElementById("page-loader")

window.addEventListener("load", ()=>{
    setTimeout(()=>{
        pageLoader.style.display = "none"
        
    }, 800)
})