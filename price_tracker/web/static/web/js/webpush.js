// Based On https://github.com/chrisdavidmills/push-api-demo/blob/283df97baf49a9e67705ed08354238b83ba7e9d3/main.js

var isPushEnabled = false,
    registration;

let webpush_url, webpush_group, webpush_vapid;
webpush_state = {str: ''}

window.addEventListener('load', function() {
  webpush_url   = document.querySelector('meta[name="webpush-save-url"]').content;
  webpush_group = document.querySelector('meta[name="webpush-group"]').content;
  webpush_vapid = document.querySelector('meta[name="webpush-vapid-key"]').content;

  // Do everything if the Browser Supports Service Worker
  if ('serviceWorker' in navigator) {
    const serviceWorker = document.querySelector('meta[name="service-worker-js"]').content;
    navigator.serviceWorker.register(serviceWorker).then(
      function(reg) {
        registration = reg;
        initialiseState(reg);
      });
  }
  // If service worker not supported
  else {
    webpush_state.str = 'Service workers are not supported in your browser.';
  }

  // Once the service worker is registered set the initial state
  function initialiseState(reg) {
    // Are Notifications supported in the service worker?
    if (!(reg.showNotification)) {
      webpush_state.str = 'Showing notifications are not supported in your browser.';
      return;
    }

    // Check the current Notification permission.
    // If its denied, it's a permanent block until the
    // user changes the permission
    if (Notification.permission === 'denied') {
      webpush_state.str = 'Push notifications are blocked by your browser.';
      return;
    }

    // Check if push messaging is supported
    if (!('PushManager' in window)) {
      webpush_state.str = 'Push notifications are not available in your browser.';
      return;
    }

    // We need to get subscription state for push notifications and send the information to server
    reg.pushManager.getSubscription().then(
      function(subscription) {
        if (subscription){
          postSubscribeObj('subscribe', subscription,
            function(response) {
              // Check the information is saved successfully into server
              if (response.status === 201) {
                isPushEnabled = true;
                webpush_state.str = 'Successfully subscribed to push notifications.';
              }
            });
        }
      });
  }
});

function subscribe(reg, callback) {
  // Get the Subscription or register one
  reg.pushManager.getSubscription().then(
    function(subscription) {
      var applicationServerKey, options;
      // Check if Subscription is available
      if (subscription) {
        return subscription;
      }

      applicationServerKey = webpush_vapid;
      options = {
        userVisibleOnly: true
      };
      if (applicationServerKey){
        options.applicationServerKey = urlB64ToUint8Array(applicationServerKey)
      }
      // If not, register one
      reg.pushManager.subscribe(options)
        .then(
          function(subscription) {
            postSubscribeObj('subscribe', subscription,
              function(response) {
                // Check the information is saved successfully into server
                if (response.status === 201) {
                  isPushEnabled = true;
                  webpush_state.str = 'Successfully subscribed to push notifications.';
                  callback(isPushEnabled);
                }
              }
            )
          }
        )
        .catch(
          function() {
            console.log('Error while subscribing to push notifications.', arguments);
            callback(isPushEnabled);
          });
    }
  );
}

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function unsubscribe(reg) {
  // Get the Subscription to unregister
  reg.pushManager.getSubscription()
    .then(
      function(subscription) {

        // Check we have a subscription to unsubscribe
        if (!subscription) {
          // No subscription object, so set the state
          // to allow the user to subscribe to push
          webpush_state.str = 'Subscription is not available.';
          return;
        }
        postSubscribeObj('unsubscribe', subscription,
          function(response) {
            // Check if the information is deleted from server
            if (response.status === 202) {
              // Get the Subscription
              // Remove the subscription
              subscription.unsubscribe()
                .then(
                  function(successful) {
                    webpush_state.str = 'Successfully unsubscribed from push notifications.';
                    isPushEnabled = false;
                  }
                )
                .catch(
                  function(error) {
                    webpush_state.str = 'Error while unsubscribing from push notifications.';
                  }
                );
            }
          });
      }
    )
}

function postSubscribeObj(statusType, subscription, callback) {
  // Send the information to the server with fetch API.
  // the type of the request, the name of the user subscribing,
  // and the push subscription endpoint + key the server needs
  // to send push messages

  var browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase(),
    data = {status_type: statusType,
              subscription: subscription.toJSON(),
              browser: browser,
              group: webpush_group
           };

  fetch(webpush_url, {
    method: 'post',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
    credentials: 'include'
  }).then(callback);
}
