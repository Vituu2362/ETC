var app = angular.module('myapp', []);

app.controller('myappCtrl', function($scope, $http) {
    $scope.AddData = function() {
        var data = {
            pass_type: $scope.field_10,
            period: $scope.field_12,
            toll_name: $scope.field_2,
            vehicle_number: $scope.field_5,
            owner_name: $scope.field_3,
            mobile_number: $scope.field_7,
            amount: $scope.field_11
        };

        $http.post('/add_toll_pass', data)
            .then(function(response) {
                alert('Toll Pass Applied Successfully');
            }, function(error) {
                alert('Error applying Toll Pass');
            });
    };
});
