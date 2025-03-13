document.addEventListener('DOMContentLoaded', function() {
    var productIdElement = document.querySelector('#product-info');
    var productId = productIdElement ? productIdElement.getAttribute('data-product-id') : null;

    if (productId) {
        initializeBidSocket(productId);
    } else {
        console.error('Product ID not found');
    }

    initializeNotificationSocket();

    function initializeBidSocket(productId) {
        var bidSocket = new WebSocket(`ws://${window.location.host}/ws/bid/${productId}/`);

        bidSocket.onopen = function(e) {
            console.log('Bid socket opened:', e);
        };

        bidSocket.onmessage = function(e) {
            try {
                var data = JSON.parse(e.data);
                var bid = data.bid;
                console.log('New bid received:', bid);
                // Update the UI with the new bid
            } catch (error) {
                console.error('Error parsing bid message:', error);
            }
        };

        bidSocket.onclose = function(e) {
            console.error('Bid socket closed unexpectedly', e);
            setTimeout(() => initializeBidSocket(productId), 5000); // Retry after 5 seconds
        };

        bidSocket.onerror = function(e) {
            console.error('Bid socket encountered error', e);
        };

        var placeBidButton = document.querySelector('#placeBid');
        if (placeBidButton) {
            placeBidButton.addEventListener('click', function() {
                var bidAmountElement = document.querySelector('#bidAmount');
                if (bidAmountElement) {
                    var bidAmount = bidAmountElement.value;
                    if (bidAmount) {
                        try {
                            bidSocket.send(JSON.stringify({ 'bid': bidAmount }));
                            console.log('Bid sent:', bidAmount);
                        } catch (error) {
                            console.error('Error sending bid:', error);
                        }
                    } else {
                        console.error('Bid amount is empty');
                    }
                } else {
                    console.error('Bid amount element not found');
                }
            });
        } else {
            console.error('Place bid button not found');
        }
    }

    function initializeNotificationSocket() {
        var notificationSocket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);

        notificationSocket.onopen = function(e) {
            console.log('Notification socket opened:', e);
        };

        notificationSocket.onmessage = function(e) {
            try {
                var data = JSON.parse(e.data);
                var notification = data.notification;
                console.log('New notification:', notification);

                var notificationList = document.querySelector('#notification-list');
                if (notificationList) {
                    var newItem = document.createElement('div');
                    newItem.classList.add('list-group-item');
                    newItem.textContent = notification;
                    notificationList.appendChild(newItem);
                } else {
                    console.error('Notification list element not found');
                }

                showRealTimeNotification(notification);
            } catch (error) {
                console.error('Error parsing notification message:', error);
            }
        };

        notificationSocket.onclose = function(e) {
            console.error('Notification socket closed unexpectedly', e);
            setTimeout(initializeNotificationSocket, 5000); // Retry after 5 seconds
        };

        notificationSocket.onerror = function(e) {
            console.error('Notification socket encountered error', e);
        };
    }

    function showRealTimeNotification(notification) {
        var notificationContainer = document.createElement('div');
        notificationContainer.classList.add('fixed', 'right-4', 'bottom-4', 'bg-white', 'shadow-lg', 'rounded-lg', 'p-4', 'max-w-xs', 'z-50');
        notificationContainer.innerHTML = `<div class="flex justify-between items-start">
            <div class="flex items-center">
                <span class="bg-blue-500 text-white rounded-full h-8 w-8 flex items-center justify-center">
                    <i class="fas fa-bell"></i>
                </span>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">New Bid Notification</p>
                    <p class="text-sm text-gray-500">${notification}</p>
                </div>
            </div>
            <button class="ml-4 text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>`;

        document.body.appendChild(notificationContainer);

        setTimeout(() => {
            notificationContainer.remove();
        }, 5000);
    }
});
