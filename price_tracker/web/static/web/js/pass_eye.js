window.addEventListener('load', function(){
    var pass_eyes = document.querySelectorAll('.pass_eye');
    pass_eyes.forEach((pass_eye)=>{
        pass_eye.addEventListener('click', (event)=>{
            var input = event.currentTarget.previousElementSibling;
            if (input.getAttribute('type') == 'password') {
                pass_eyes.forEach((pass_eye)=>{
                    pass_eye.classList.add('pass_eye_line');
                    pass_eye.previousElementSibling.setAttribute('type', 'text');
                });            
            } else {
                pass_eyes.forEach((pass_eye)=>{
                    pass_eye.classList.remove('pass_eye_line');
                    pass_eye.previousElementSibling.setAttribute('type', 'password');
                });
            }
        })
    });
});