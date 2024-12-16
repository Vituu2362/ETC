var app = angular.module('myapp', ['ngCookies']);

app.controller('myappCtrl', function($scope, $http) {
    // Fetch admin details from the Flask backend
    $http.get('/api/admin-details')
        .then(function(response) {
            $scope.admindetails = [response.data]; // Assign the received data to admindetails
        }, function(error) {
            console.error('Error fetching admin details:', error);
        });

    // Function to handle updating password (dummy for now)
    $scope.admin_update_info = function(password) {
        console.log('Edit password clicked for: ' + password);
    };
});