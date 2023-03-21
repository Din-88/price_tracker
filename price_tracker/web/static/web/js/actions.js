
const hide_drag_els = () => {
    [... drag_containers[0].children].forEach((tracker) => {
        tracker.querySelector('.tc-h-dad > .ion-arrow-move').classList.add('visually-hidden');
    });
}
const show_drag_els = () => {
    [... drag_containers[0].children].forEach((tracker) => {
        tracker.querySelector('.tc-h-dad > .ion-arrow-move').classList.remove('visually-hidden');
    });
}

const show_section_trackers = () => {
    el_tracker_new.classList.add('visually-hidden');
    el_settings.classList.add('visually-hidden');
    el_tracker_my.classList.remove('visually-hidden');
}
const show_section_new = () => {
    el_tracker_my.classList.add('visually-hidden');
    el_settings.classList.add('visually-hidden');
    el_tracker_new.classList.remove('visually-hidden');
}
const show_section_settings = () => {
    el_tracker_my.classList.add('visually-hidden');
    el_tracker_new.classList.add('visually-hidden');
    el_settings.classList.remove('visually-hidden');
}

const data_sort_by_price = (tracker_a, tracker_b) => {
    var price_a = tracker_a.querySelector('.tc-h-price').textContent;
    var price_b = tracker_b.querySelector('.tc-h-price').textContent;
    price_a = parseFloat(price_a);
    price_b = parseFloat(price_b)
    return [price_a?price_a:0, price_b?price_b:0];
}

const data_sort_by_update = (tracker_a, tracker_b) => {
    let el_card_header_a = tracker_a.querySelector('.card-body').children[0];
    let el_card_header_b = tracker_b.querySelector('.card-body').children[0];

    var date_a = el_card_header_a.querySelector("div:nth-child(1)>span").getAttribute('date');
    var date_b = el_card_header_b.querySelector("div:nth-child(1)>span").getAttribute('date');

    // date_a = new Date(date_a).getTime();
    // date_b = new Date(date_b).getTime();
    
    date_a = Date.parse(date_a);
    date_b = Date.parse(date_b);

    return [date_a, date_b];
}

const sort_trackers = (data_sort, ascending) => {
    var trackers = [... drag_containers[0].children];
    var ids = [];

    trackers.sort((tracker_a, tracker_b) => {
        data = data_sort(tracker_a, tracker_b)
        if (ascending) { 
            return data[0] - data[1];
        } else {
            return data[1] - data[0];
        }
    }).forEach((tracker) => {
        ids.push(tracker.getAttribute('sort-id'));
    });

    return ids;    
}

const action_my_tracker = () => {
    show_drag_els();
    show_section_trackers();
    
    sor[0].option("disabled", false);
    let order = localStorage.getItem(sor[0].options.group.name);
    order = order ? order.split('|') : [];
    sor[0].sort(order, true);
}

let price_ascending = true;
const action_by_price = (event) => {
    hide_drag_els();
    show_section_trackers();

    sor[0].option("disabled", true);
    let ids = sort_trackers(data_sort_by_price, price_ascending);
    sor[0].sort(ids, true);
    price_ascending = !price_ascending;
}

let update_ascending = true;
const action_by_update = () => {
    hide_drag_els();
    show_section_trackers();

    sor[0].option("disabled", true);
    let ids = sort_trackers(data_sort_by_update, update_ascending);
    sor[0].sort(ids, true);
    update_ascending = !update_ascending;
}

let tracker_body_show = true;
const action_collapse = () => {
    if (tracker_body_show) {
        collapseList.map(el => el.hide());
    } else {
        collapseList.map(el => el.show());
    }

    tracker_body_show = !tracker_body_show;
}

const action_update_all = () => {
    Trackers.forEach((tracker) => {
        Api.update(pk)
        .then((data) => {
            update_el_tracker(tracker, data);
        })
        .catch(err => {
            console.log(err)
        });
    })
    show_section_trackers();
}

const action_new_tracker = () => {
    show_section_new();
}

const action_settings = () => {
    show_section_settings();
}

const offcanvas_nav_click = (event) => {
    event.preventDefault();
    switch (event.target.id) {
        case 'act_my_trackers':
            action_my_tracker(event); break;
        case 'act_by_price':
            action_by_price(event); break;
        case 'act_by_update':
            action_by_update(event); break;
        case 'act_collapse':
            action_collapse(event); break;
        case 'act_update_all':
            action_update_all(event); break;
        case 'act_new_tracker':
            action_new_tracker(event); break;
        case 'act_settings':
            action_settings(event); break;
        default:
            console.log(`Sorry.`); break;
    }
}

// var el_spinner = document.createElement("span");
// el_spinner.classList.add('spinner-border');
// el_spinner.classList.add('spinner-border-sm');
// el_spinner.setAttribute('role', 'status');

function t_opt_upd(el, pk) {
    Api.update(pk)
    .then((data) => {
        trackers[pk].el_update(data.info);

        el.disabled = false;
        el.parentElement.classList.remove('blur');
    });
}

function t_opt_730(el, pk, is_new) {
    if (is_new) { pk = 'new'; }
    days = el.checked ? 30 : 7;
    trackers[pk].chart_update_d(days);
    
    el.disabled = false;
    el.parentElement.classList.remove('blur');
}

function t_opt_not(el, pk) {
    Api.notify(pk, el.checked)
    .then((data) => {
        el.disabled = false;
        el.checked = data.notify;
        el.parentElement.classList.remove('blur');
    });   
}

function t_opt_add(el, pk, is_new) {
    Api.add_for_user(pk)
    .then((data) => {
        if (data.add_for_user === 'ok') {
            if (is_new) {
                if (!(pk in trackers)) {
                    trackers[pk] = new Tracker(pk, is_user=true, is_new=false);
                    drag_containers[0].prepend(trackers[pk].el);
                    var el_coll = trackers[pk].el.querySelector('.collapse')
                    var bs_c = new bootstrap.Collapse(el_coll, {togle: true});
                    collapseList.push(bs_c);
                }
                trackers['new'].is_user = true;
                trackers['new'].data.is_user = true;
                trackers[pk].el_update(trackers['new'].data);                
            } else {
                trackers[pk].is_user = true;
                if (trackers['new'].pk == pk) {
                    trackers['new'].is_user = true;
                }
            }
        }
        
        el.disabled = false;
        el.parentElement.classList.remove('blur');
    });
}

function t_opt_del(el, pk, is_new) {
    Api.del_for_user(pk)
    .then((data) => {
        if (data.del_for_user === 'ok') {
            if (pk in trackers) {
                trackers[pk].is_user = false;
            }            
            if (trackers['new'].pk == pk) {
                trackers['new'].is_user = false;
            }
            if (!(document.location.pathname === '/')) {
                drag_containers[0].removeChild(trackers[pk].el);
                delete trackers[pk];
            }
        }

        el.disabled = false;
        el.parentElement.classList.remove('blur');
    })
}

const tracker_option_actions = (event) => {
    let el = event.currentTarget;

    el.disabled = true;
    el.parentElement.classList.add('blur');

    let [action, pk, is_new, is_user] = el.id.split('_');
    
    let el_t = el.closest('.col');
    
    switch(action){
        case 'b-u':
            t_opt_upd(el, pk); break;
        case 'sw-d':
            t_opt_730(el, pk, is_new); break;
        case 'sw-n':
            t_opt_not(el, pk); break;
        case 'b-a':
            t_opt_add(el, pk, is_new); break;
        case 'b-d':
            t_opt_del(el, pk, is_new); break;
        default:
            console.log('sorry'); break;
    }
}


const action_send_new_tracker = (event) => {
    event.preventDefault();
    let form_data = new FormData(event.target);    
    let data = Object.fromEntries(form_data.entries());

    Api.new_tracker(data=data)
    .then((data) => {
        if ('error' in data){
            if(data.error.data.error === 'url unknown'){
                show_alert('В настоящий момент мы не можем обрабодать данный url.', 'new-trecker-alert')
            }
            return;
        }   
        console.log(data);
        trackers['new'].el_update(data.info);
	})
    .catch((error) => {
        console.log(error);
    });
}