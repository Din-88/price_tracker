
class Api {
    static api_fetch_post(url, data, method='POST') {
        return fetch(url, {
            method: method,
            credentials: 'same-origin',
            headers:{
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(data)
        })
        .then((response) => response.json())
    }

    static api_fetch_get(url) {
        return fetch(url, {
            method: 'Get',
            credentials: 'same-origin',
            headers:{
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
        })
        .then((response) => response.json())
    }

    static api_fetch_form(url, data) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers:{
                'Accept': 'application/json',
                // 'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            body: data,
        })
        .then((response) => response.json())
    }
    
    static get(pk) {
        return this.api_fetch_get(`/api/tracker/${pk}/get/`);
    }
    
    static new_tracker(data={}) {
        return this.api_fetch_post('/api/tracker/new/', data);
    }
    
    static update(pk) {
        return this.api_fetch_get(`/api/tracker/${pk}/update/`);
    }

    static add_for_user(pk) {
        return this.api_fetch_get(`/api/add/${pk}`);
    }

    static del_for_user(pk) {
        return this.api_fetch_get(`/api/del/${pk}`);
    }

    static notify(pk, notifi=false) {
        var data = {'notify': notifi};
        return this.api_fetch_post(`/api/notify/${pk}`, data, 'PATCH');
    }

    static basics(data) {
        if(data) {
            return this.api_fetch_post(`/api/basics/`, data, 'PATCH');
        }
        return this.api_fetch_get('/api/basics/');
    }

    static social_disconnect(pk) {
        return this.api_fetch_post(`/socialaccounts/${pk}/disconnect/`);
    }

    static user_notify() {
        return this.api_fetch_get('/api/user_notify/');
    }
}