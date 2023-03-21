class Tracker {
    static EL_TRACKER = document.getElementById('tracker');

    constructor(pk, is_user=false, is_new=false) {
        this.pk = pk;
        this.els = {};
        this.data = {};
        this.el = this.el_create(pk, is_user, is_new);
        this.is_new  = is_new;
        this.is_user = is_user;
        this.chart;
        this.chart_create();
    }

    set is_user(is_user) {
        this.data.is_user = true;
        this.el_create_options(this.el, this.pk, is_user);
    }

    sw_n(checked=false){
        this.els.el_sw_n.children[0].checked = checked;
    }

    el_create_options(el, id, is_user=false, is_new=this.is_new) {
        this.is_new = is_new;
        let tracker_options = el.querySelector('div[tracker-options]');

        let labels = tracker_options.querySelectorAll('label');
        this.els.el_sw_d = labels[0];
        this.els.el_sw_n = labels[1];

        let post_id = `_${id}` + (is_new?'_new':'_') + (is_user?'_user':'_');

        this.els.el_sw_d.setAttribute('for', 'sw-d' + post_id);
        this.els.el_sw_n.setAttribute('for', 'sw-n' + post_id);

        this.els.el_sw_d.children[0].id = 'sw-d' + post_id;
        this.els.el_sw_n.children[0].id = 'sw-n' + post_id;

        this.els.buttons = tracker_options.querySelectorAll('button');
        this.els.buttons[0].id = 'b-d' + post_id;
        this.els.buttons[1].id = 'b-a' + post_id;
        this.els.buttons[2].id = 'b-u' + post_id;

        if (is_user) {
            this.els.buttons[1].classList.add('visually-hidden');
            this.els.buttons[0].classList.remove('visually-hidden');
            this.els.el_sw_n.children[0].checked = true;
            this.els.el_sw_n.children[0].disabled = false;
        } else {
            this.els.buttons[0].classList.add('visually-hidden');
            this.els.buttons[1].classList.remove('visually-hidden');
            this.els.el_sw_n.children[0].checked = false;
            this.els.el_sw_n.children[0].disabled = true;
        }

        return [this.els.el_sw_d.children[0], this.els.el_sw_n.children[0], ...this.els.buttons];
    }

    el_create(id, is_user=false, is_new=false) {
        let el = Tracker.EL_TRACKER.cloneNode(true);
        el.id = "";
        el.setAttribute('sort-id', id);
        if (!is_new) {
            el.children[0].children[1].id = `collapse-content-${id}`;
            el.children[0].children[0].children[0].setAttribute('aria-controls', `collapse-content-${id}`);
            el.children[0].children[0].children[0].setAttribute('data-bs-target', `#collapse-content-${id}`);
        }
    
        this.el_create_options(el, id).forEach((o) => {
            o.addEventListener('click', (event) => {
                tracker_option_actions(event);
            });
        });        
        
        this.els.el_card_header = el.querySelector('.card-header');

        this.els.el_h     = this.els.el_card_header.querySelector("h6");
        this.els.el_prev  = this.els.el_card_header.querySelector("img");
        this.els.el_price = this.els.el_card_header.querySelector("span");

        this.els.el_card_body = el.querySelector('.card-body').children[0];

        this.els.el_host = this.els.el_card_body.querySelector("div:nth-child(1)>a");
        this.els.el_date = this.els.el_card_body.querySelector("div:nth-child(1)>span");
        this.els.el_img  = this.els.el_card_body.querySelector("div:nth-child(4)>img");
        this.els.el_url  = this.els.el_card_body.lastElementChild.children[0];

        if (is_new) {
            let img = el.querySelector('.tc-b-div-img');
            img.classList.add('tcn-b-div-img');
            img.children[0].style.maxHeight = '130px';

            let div_chart = el.querySelector('.tc-div-chart');
            div_chart.classList.add('tcn-div-chart');
        } else {
            let img = el.querySelector('.tc-b-div-img');
            img.classList.remove('tcn-b-div-img');
            img.children[0].style.maxHeight = '100px';

            let div_chart = el.querySelector('.tc-div-chart');
            div_chart.classList.remove('tcn-div-chart');
        }
        
        el.classList.remove('visually-hidden');
        return el;
    }

    chart_create() {
        let canvas = this.el.querySelector('canvas');
        this.chart = new Chart(canvas, {
            type: 'line',
            data: {
                // labels: labels,
                datasets: [{
                    // label: "123456",
                    lineTension: 0.1,
                    bezierCurve : false,
                    borderColor: "#3e95cd",
                    backgroundColor: "#7bb6dd",
                    pointBorderColor: "rgba(62,149,205,0.9)",
                    pointBackgroundColor: "rgba(62,149,205,0.9)",
                    pointRadius: 2,
                    pointHoverRadius: 4,
                    fill: false,
                    // data: data,
                    pointStyle: 'circle',
                }],
            },
            options: {
                scales: {
                    xAxes: [{
                        ticks: {
                            display: false
                        },
                        type: "time",
                        time: {
                            unit: 'day',
                            round: 'day',                                                                                                                                                                           
                            tooltipFormat: 'DD-MM-YYYY HH:mm',
                            displayFormats: {
                                millisecond: 'HH:mm:ss.SSS',
                                second: 'HH:mm:ss',
                                minute: 'HH:mm',
                                hour: 'HH',
                                day: 'DD'
                            },
                        },                      
                    }],
                    yAxes: [ {
                        ticks: {
                          display: true
                        }
                      } ]
                },
                parsing: {
                    xAxisKey: 'date_time',
                    yAxisKey: 'price'
                },
                legend: {
                    display: false
                },
                layout: {
                    padding: {
                        right: 5
                    }
                },
                tooltip: {
                    usePointStyle: true,
                },
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }

    chart_update(data) {
        let prices = data.prices;
        let labels = prices.map((d) => new Date(d.date_time));
        let c_data = prices.map((d) => parseFloat(d.price));

        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = c_data;
        this.chart.update()
    }

    chart_update_d(days) {
        let prices = this.data.prices;
        let a = new Date().setDate(new Date().getDate() - days);
        let n = prices.filter(p => {
            let b = new Date(p.date_time).getTime();
            return b >= a;
        });

        let labels = n.map((d) => new Date(d.date_time));
        let data   = n.map((d) => parseFloat(d.price));
        
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = [];
        data.forEach((d) => { this.chart.data.datasets[0].data.push(d); this.chart.update(); });
        // this.chart.data.datasets[0].data = data;
        this.chart.update()
    }

    el_data_update(data) {
        this.el.setAttribute('t-pk', data.pk)
        
        if (data.prices.length > 0) {
            let avg_price = data.prices.reduce((a, b, idx) => a + (parseFloat(b['price']) ? parseFloat(b['price']) : a/idx) , 0) / data.prices.length;

            let curr_price = parseFloat(data.prices[0].price);

            if (!curr_price) {
                this.els.el_prev.classList.add('neon-red');
            } else if (curr_price <= avg_price) {
                this.els.el_prev.classList.add('neon-green');
            } else if (curr_price > avg_price) {
                this.els.el_prev.classList.add('neon-yellow');
            }
        }

        if(data.hasOwnProperty('notifi')) {
            this.els.el_sw_n.children[0].checked = data.notifi;
        }

        this.els.el_host.href       = "https://" + data.host;
        this.els.el_host.innerText  = data.host;
        this.els.el_date.setAttribute('date', data.date_time);
        this.els.el_date.innerText  = new Date(data.date_time).toLocaleString('ru-Ru');
        this.els.el_h.innerText     = data.title;
        this.els.el_price.innerHTML = data.price ? data.price : "None";
        this.els.el_url.href        = data.url;
        this.els.el_url.innerText   = data.url;    
        this.els.el_prev.src        = data.img_url;
        this.els.el_img.src         = data.img_url;
    }

    el_update(data) {
        // console.time('el_update');
        // console.timeEnd('el_update');
        this.data = data;
        this.is_user = data.is_user;
        this.chart_update(data);
        this.el_data_update(data);
    }
}