app.controller('YourController', function($scope, $window) {
    $scope.user_logout = function() {
        // Clear user session (this depends on how you handle authentication)
        sessionStorage.removeItem('userToken'); // Example of removing token

        // Optionally clear other data like cookies or local storage
        localStorage.clear(); // Clears all localStorage

        // Redirect to login page or homepage
        $window.location.href = '/login'; // Redirect to login page
    };
});