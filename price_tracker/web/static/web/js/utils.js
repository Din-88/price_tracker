let show_alert;

window.addEventListener('load', function(){
    let el_alert = document.getElementById('top-alert');

    show_alert = (message, el_alert_id) => {
        let wrapper = document.createElement('div');
        wrapper.className = 'alert alert-${type} alert-dark alert-dismissible fade show text-center';
        wrapper.role = 'alert';
        wrapper.innerHTML = `
            <div>${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
        
        if(el_alert_id){
            document.getElementById(el_alert_id).append(wrapper);
            return;
        }
        el_alert.append(wrapper);
    }
})