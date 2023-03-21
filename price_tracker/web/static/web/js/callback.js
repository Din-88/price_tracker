function callback() {    
    let code = new URL(window.location.href).searchParams.get('code');
    
    fetch('/api/google/connect/', {
        method: 'POST',
        credentials: 'same-origin',
        headers:{
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ code: code})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        localStorage.setItem("social_auth", JSON.stringify(data));
        window.close();
    })
    .catch(error => {
        console.log(error);
        data = {'error': {data: error}};
        localStorage.setItem("social_auth", JSON.stringify(data));
        window.close();
    });
}

callback();