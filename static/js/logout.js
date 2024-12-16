$scope.user_logout = function() {
    $http.get('/logout')
    .then(function(response) {
        if (response.status === 200) {
            window.location.href = '/welcome'; // Redirect to welcome page after successful logout
        }
    })
    .catch(function(error) {
        console.error('Logout failed:', error);
        alert('Failed to log out. Please try again.');
    });
};
