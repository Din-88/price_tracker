
const sortable = (container) => {
    return new Sortable(container, {
        handle: '.ion-arrow-move',
        delay: 100,
        touchStartThreshold: 3,
        delayOnTouchOnly: "true",
        group: 'shared',
        dataIdAttr: 'sort-id',
        animation: 200,
        swapThreshold: 0.65,
        fallbackOnBody: true,
        preventOnFilter: false,
        sort: true,
        onEnd: function (/**Event*/evt) {
            var itemEl = evt.item;  // dragged HTMLElement
            evt.to;    // target list
            evt.from;  // previous list
            evt.oldIndex;  // element's old index within old parent
            evt.newIndex;  // element's new index within new parent
            evt.oldDraggableIndex; // element's old index within old parent, only counting draggable elements
            evt.newDraggableIndex; // element's new index within new parent, only counting draggable elements
            evt.clone // the clone element
            evt.pullMode;  // when item is in another sortable: `"clone"` if cloning, `true` if moving

            if ('tracker-container' in evt.to.attributes) {
                // foto_insert(el_to=evt.to, item=evt.item);
                fotos_priviews_update(tracker_container=evt.to);
            }
            if ('tracker-container' in evt.from.attributes) {
                // foto_delete(el_from=evt.from, item=evt.item);
                fotos_priviews_update(tracker_container=evt.from);
            }
        },
        store: {
            /**
             * Get the order of elements. Called once during initialization.
             * @param   {Sortable}  sortable
             * @returns {Array}
             */
            get: function (sortable) {
                var order = localStorage.getItem(sortable.options.group.name);
                console.log(order);
                var o = order ? order.split('|') : [];
                return o;
            },

            /**
             * Save the order of elements. Called onEnd (when the item is dropped).
             * @param {Sortable}  sortable
             */
            set: function (sortable) {
                var order = sortable.toArray();
                console.log(order);
                var o = order.join('|');
                localStorage.setItem(sortable.options.group.name, o);
            }
        },
    });
}