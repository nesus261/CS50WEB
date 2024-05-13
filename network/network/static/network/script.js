
document.addEventListener('DOMContentLoaded', () => {
    switch (location.pathname)
    {
        case "/":
            document.querySelector("#v-tabs-all-tab").className += ' active'; 
            break;
        case "/login":
            document.querySelector("#v-tabs-login-tab").className += ' active'; 
            break;
        case "/register":
            document.querySelector("#v-tabs-register-tab").className += ' active'; 
            break;
        case "/followed":
            document.querySelector("#v-tabs-followed-tab").className += ' active'; 
            break;
    }
});
document.addEventListener('scroll', () => {
    dont_scroll_left_bar();
});
document.addEventListener('scrollend', () => {
    dont_scroll_left_bar();
});
function dont_scroll_left_bar()
{
    $('.left-bar')[0].style.top = window.scrollY+'px';
}
function getToken() {
    return document.cookie.split('csrftoken=')[1].split(';')[0];
}