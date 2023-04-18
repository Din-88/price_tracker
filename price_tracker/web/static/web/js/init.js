
let el_tracker_ids;
let tracker_ids;

let el_tracker;
let el_tracker_my;
let el_tracker_new;
let el_settings;
let el_form_new_tracker;
let drag_containers;

let account;
let offcanvas_nav;

let left_nav_tabs;
let sor = [];

let trackers = {};
let collapseList = [];


window.addEventListener('load', function(){
	
	let last_update = localStorage.getItem('beta_messege_date_time') || '0';
	last_update = new Date(last_update);
	let curr_time = new Date();
	if (curr_time > last_update.setHours(last_update.getHours() + 24)){
		localStorage.setItem('beta_messege_date_time', curr_time);
		show_alert(`Внимание! Сайт находится в ранней бета-версии, что означает, 
		что он находится в активной разработке и может быть изменен в будущем. 
		Просим проявить терпение, если что-то (или все) не работает должным образом. 
		<br />Благодарим за понимание!`, 'top-alert');
	}

	el_tracker_ids = document.getElementById('tracker_ids');
	tracker_ids = el_tracker_ids.textContent.split(',').map(Number).slice(0, -1);

	el_tracker     = document.getElementById('tracker');
	el_tracker_my  = document.getElementById('tracker_my');
	el_tracker_new = document.getElementById('tracker_new');
	el_settings    = document.getElementById('settings');


	drag_containers = document.querySelectorAll('div[drag-column]');

	el_form_new_tracker = document.querySelector('#f_new_tracker');

	el_form_new_tracker.addEventListener('submit', (event) => {
		action_send_new_tracker(event);
	});

	sor[0] = sortable(drag_containers[0]);

	trackers = {};
	trackers['new'] = new Tracker(pk=tracker_ids[0], is_user=false, is_new=true);

	el_tracker_new.querySelector('.col-md-9').appendChild(trackers['new'].el);

	Api.get(trackers['new'].pk)
	.then((data) => {
		trackers['new'].el_update(data.info);
		trackers['new'].el.querySelector('.collapse').classList.add('show');
	});
	

	tracker_ids.forEach((id) => {
		
		if (document.location.pathname === '/') {
			trackers[id] = new Tracker(pk=id, is_user=false, is_new=false);
		} else {
			trackers[id] = new Tracker(pk=id, is_user=true, is_new=false);
		}
		
		drag_containers[0].appendChild(trackers[id].el);

		Api.get(id)
		.then((data) => {
			trackers[id].el_update(data.info);
			// trackers[id].is_user = json.is_user;

			var el_coll = trackers[id].el.querySelector('.collapse')
			var bs_c = new bootstrap.Collapse(el_coll, {togle: true});
			collapseList.push(bs_c);
		});
	});
});

