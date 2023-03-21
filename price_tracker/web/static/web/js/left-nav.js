
class LeftNavTabs{
    constructor(id_list) {
        this.id_list = id_list;
        this.el_list = document.getElementById(id_list);

        this.el_list.addEventListener('click', (event)=>{
            event.preventDefault();
            let el = event.target.parentElement;
        
            if (!el.hasAttribute('no_fix')){
                this.deactivate_sibling_down(el);
            }
            
            this.deactivate_up(el);
            this.active_parents(el);
        });
    }

    deactivate_down(el) {
        el.classList.remove('active');
        let elms = [...el.children];
        elms.forEach((e) => {
            this.deactivate_down(e);
        })
    }
    
    deactivate_sibling_down(el) {
        let elms = [...el.parentElement.children];
        elms.forEach((e) => {
            this.deactivate_down(e);
        })
    }
    
    deactivate_up(el) {
        if(el.parentElement.id !== this.id_list) {
            let elms = [...el.parentElement.parentElement.parentElement.children].filter(e => e !== el.parentElement.parentElement);
            elms.forEach((e) => {
                this.deactivate_down(e);
                this.deactivate_up(e);
            })
        }
    }
    
    active_parents(el) {
        if (!el.hasAttribute('no_fix')){
            el.classList.add('active');
        }
        
        if(el.parentElement.id !== 'nav_list') {
            this.active_parents(el.parentElement);
        }
    }
}