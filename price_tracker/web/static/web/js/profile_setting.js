
let object_entries = (obj, depth=0) => {
    let ret=[];    
    let f=(o)=>{
        Object.entries(o).forEach(([k, v])=>{
            if(typeof v === 'object' && !(v instanceof Array) && depth>0){
                depth--;
                f(v);
            } else {
                ret.push([k, v]);
            }
        })
    }
    f(obj);
    return ret;
}

let filteredObj = (obj, callback) => {
    let newObj = {};
    for (let [key, value] of Object.entries(obj)) {
        if (callback(value, key, obj)) {
            newObj[key] = value;
        }
    }
    return newObj;
}


class Account {
    constructor(el){
        this.el = el;
        this.els = {};
        this.els.forms = this.el.querySelectorAll('#f_basics, #f_account, #f_notify');
        this.els_errors = {};
        this.data = {};
        this.find_elements();
        this.api_update();
        this.listeners();

        this.els.push_warn = this.el.querySelector('#push-worning');

        // webpush_state = new Proxy(webpush_state, {
        //     set(target, key, value, receiver) {
        //         let success = Reflect.set(...arguments); 
        //         if (success) { 
        //             l.textContent = value;
        //         }
        //         return success;
        //     }
        // });
        // let l = document.createElement('div');
        // document.querySelector('body').insertAdjacentElement('afterbegin', l);
    }

    listeners(){
        this.els.forms.forEach((form)=>{
            form.addEventListener('submit', (event)=>{
                event.preventDefault();
    
                let form_data = new FormData(event.target);    
                let data_obj = Object.fromEntries(form_data.entries());    
                data_obj = filteredObj(data_obj, value=>value!=='');
    
                data_obj.trackers_settings = {};
    
                let notify_types_els = event.target.elements["notify_types"];
                if(notify_types_els) {
                    data_obj.trackers_settings.notify_types = Array.prototype.filter.call(notify_types_els, el => el.checked).map(el => el.value);
                    delete data_obj.notify_types;
                }
    
                if(data_obj.notify_case){
                    data_obj.trackers_settings.notify_case = data_obj.notify_case;
                    delete data_obj.notify_case;
                }
    
                event.target.querySelector('fieldset').disabled = true;
                Api.basics(data_obj)
                .then((data) => {
                    this.update(data);
                    event.target.querySelector('fieldset').disabled = false;            
                })
                .catch((error) => {
                    console.log(error);
                    event.target.querySelector('fieldset').disabled = false; 
                });
            });
        });

        this.el.querySelectorAll('button[type="button"]').forEach((b)=> {
            b.addEventListener('click', (event)=> {
                let fieldset = b.parentElement.parentElement.querySelector('fieldset');
                if (fieldset.disabled===true) {
                    b.innerText = 'Отменить изменения';
                    b.type='button';        
                    fieldset.disabled = false;
                } else {
                    b.innerText = 'Редактировать';
                    b.type='reset';
                    form = b.parentElement.parentElement;
                    fieldset.disabled = true;
                }        
            });
        });

        this.el.querySelector('#show_pass').addEventListener('change', (event)=> {
            var pass_inputs = event.target.offsetParent.children[2].querySelectorAll('input[type=password], input[type=text]');
            if(event.target.checked) {
                pass_inputs.forEach((input)=>{
                    input.setAttribute('type', 'text');
                })        
            } else {
                pass_inputs.forEach((input)=>{
                    input.setAttribute('type', 'password');
                })
            }
        })
    }

    api_update(){
        Api.basics()
        .then((data)=>{
            this.update(data);
        })
        .catch((error)=>{
            console.log(error);
        });
    }
    
    find_elements(){
        this.els.forms.forEach((form)=>{
            this.els = Object.assign(this.els, form.elements);
        });

        let el_tb = this.el.querySelector('tbody');
        this.els.socialaccounts = el_tb;
        
        el_tb.addEventListener('click', (event)=>{
            if (event.target.tagName === 'BUTTON') {
                Api.social_disconnect(event.target.value)
                .then((data)=> {
                    this.update(data);
                    if(data.hasOwnProperty('error')){
                                                
                    }else{
                        this.els.socialaccounts.removeChild(event.target.parentElement.parentElement);
                        this.api_update();
                    }
                })
                .catch((error) => {
                    console.log(error);
                });
            }            
        })

        let social_btns = this.el.querySelectorAll('button[provider="google"]');
        social_btns.forEach((b)=> {
            this.els['provider_' + b.attributes.provider.value] = b;
            b.addEventListener('click', (event)=> {
                let provider = event.currentTarget.attributes.provider.value;
                google().then((data)=>{
                    data.hasOwnProperty('key') ? this.api_update() : this.update(data);
                });
            });
        });
    }

    enable_push(){
        if (Notification.permission === 'granted'){
			subscribe(registration);
            this.els.push_warn.classList.add('visually-hidden');
        }
        else if (Notification.permission === 'default') {
            subscribe(registration, (isPushEnabled)=> {
					if (!isPushEnabled){
						show_alert('В настройка у вас выбранно получение уведомлений которые отключенны в вашем браузере.', 'top-alert');
						this.els.push_warn.classList.remove('visually-hidden');
					} else {
						this.els.push_warn.classList.add('visually-hidden');
					}
				});
			}
        else if (Notification.permission === 'denied') {
            unsubscribe(registration);
            this.els.push_warn.classList.remove('visually-hidden');
            show_alert('В настройка у вас выбранно получение уведомлений которые отключенны в вашем браузере.', 'top-alert')
        }
    }

    disable_push(){
        unsubscribe(registration);
        // this.els.push_warn.classList.add('visually-hidden');
    }

    update_social(value) {
        this.els.socialaccounts.innerHTML = '';
        for(let k in value){
            let v = value[k]
            let tr = document.createElement('tr');
            tr.innerHTML = `<td>${v.provider.charAt(0).toUpperCase() + v.provider.slice(1)}</td><td>${v.email}</td><td><button class="btn btn-primary btn-sm" type="button">Удалить</button></td>`;
            let button = tr.lastChild.lastChild;
            button.value = v.id;
            
            this.els.socialaccounts.appendChild(tr);
        }
    }

    update_notify(notify){
        if(notify.notify_types){
            if(notify.notify_types.some(item => item.type === 'push')){
                this.enable_push();
            } else {
                this.disable_push();
            }
        }
        object_entries(notify, 0).forEach(([key, value])=>{
            this.els[key].forEach((e)=>{
                e.checked=false;
            });
            if(!(value instanceof Array)) { value = [value] };
            for(let k in value){
                let e = Array.prototype.find.call(this.els[key], x => x.value == value[k].id);
                if(e) {e.checked = true;}
            }
        });
    }

    update(data){
        if (data.hasOwnProperty('error')) {
            this.show_errors(data.error.data);
        } else {
            this.data = Object.assign(this.data, data);
            if(data.socialaccounts) {
                this.update_social(data.socialaccounts);
                delete data.socialaccounts;
            }
            if(data.trackers_settings) {
                this.update_notify(data.trackers_settings);
                delete data.trackers_settings;
            }
            let d = object_entries(data, 1);
            d.forEach(([key, value])=>{                
                try {
                    this.els[key].value = value;
                    this.els[key].defaultValue = value;
                } catch (error) {
                    console.log(error);
                }
            })
        }
        // this.els.birth_date.setCustomValidity('chtoto ne tak');
    }

    show_errors(errors) {
        for (let k in errors) {
            let err_el = document.createElement('div');            
            err_el.textContent = errors[k];            

            if(k==='socialaccounts'){
                err_el = document.createElement('tr');
                err_el.innerHTML = `<td colspan=3>${errors[k]}</td>`;
                this.els[k].insertAdjacentElement('afterend', err_el);
            } else {
                this.els[k].parentNode.insertAdjacentElement('afterend', err_el);
            }

            err_el.style.color = 'yellow';
            err_el.className = 'pb-2';
            err_el.style.lineHeight = '1.0';
            err_el.style.fontSize = '0.8rem';
            // this.els_errors[k] = err_el;
            
            setTimeout(()=>{
                err_el.parentNode.removeChild(err_el);
            }, 10000);
        }
    }

    del_errors(_this) {
        for(let k in _this.els_errors){
            _this.els_errors[k].parentNode.removeChild(_this.els_errors[k]);
            delete _this.els_errors[k];
        }
    }
}

window.addEventListener('load', function(){
    account = new Account(el_settings);
    offcanvas_nav = document.querySelector('#offcanvas-1 .nav');
	offcanvas_nav.addEventListener('click', (event) => offcanvas_nav_click(event));
    left_nav_tabs = new LeftNavTabs('nav_list');
});

function google() {
    let client_id = '663038948523-fiie813mm7hddkq77sj548qtikn4d7fo.apps.googleusercontent.com';
    let redirectUri = encodeURIComponent(`${location.origin}/google/callback/`);
    // let redirectUri = encodeURIComponent('http://127.0.0.1:8000/google/callback/');
    // let redirectUri = 'http://127.0.0.1:8000/google/callback/';
    // let redirectUri = 'http://localhost:8000/google/callback/';
    // let redirectUri = `${location.origin}/google/callback/`;
    let url = 'https://accounts.google.com/o/oauth2/v2/auth?' +
            'response_type=code' +
            '&client_id=' + client_id +
            '&redirect_uri=' + redirectUri +
            // '&scope=' + 'https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile ' +
            //             'https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email ' + 
            //             'https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fplus.me ' +
            //             'openid' +
            '&scope=' + 'email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid' +
            // '&scope=' + encodeURIComponent('https://www.googleapis.com/auth/userinfo.email') +
            '&access_type=offline' + 
            '&state=' + '123456789645321' + 
            '&prompt=select_account';

    let win = window.open(url, '_blank');

    return new Promise((resolve, reject) => {
        let interval = setInterval(() => {
            let auth = localStorage.getItem('social_auth');
            if (auth) {
                clearInterval(interval);
                localStorage.removeItem('social_auth');
                let data = JSON.parse(auth);
                resolve(data);
            }
        }, 500);
    });
}
