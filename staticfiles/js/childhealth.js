var app = angular.module('ChildApp', ['ngSanitize']);

app.controller('ChildCtrl', ['$scope', '$http', function($scope, $http) {
        // province
        $http.get("/kiramama/reportnsc/")
        .then(function (response) {
          $scope.results = response.data.results;
      });
        $http.get("/structures/provinces/").then(function (response){
          $scope.provinces = response.data.results;
      });
        $scope.update_province = function () {
          var province = $scope.province;
          if (province) {
            $http.get("/structures/districts/?bps__code=" + province.code )
            .then(function (response) {
              $scope.districts = response.data.results;
              $http.get("/kiramama/reportnsc/?province=" + province.code )
              .then(function (response) {
                $scope.results = response.data.results;
            });
          });
        }
    };
          // district
          $scope.update_district = function () {
            var district = $scope.district;
            if (district) {
              $http.get("/structures/cds/?district__code=" + district.code )
              .then(function (response) {
                $scope.cdss = response.data.results;
                $http.get("/kiramama/reportnsc/?district=" + district.code )
                .then(function (response) {
                  $scope.results = response.data.results;
              });
            });
          }
      };
      // cds
          $scope.update_cds = function () {
            var cds = $scope.cds;
            if (cds) {
                $http.get("/kiramama/reportnsc/?cds=" + cds.code )
                .then(function (response) {
                  $scope.results = response.data.results;
              });
          }
      };

        // date
        $scope.get_bydate = function () {
          var startdate = $scope.startdate;
          var enddate = $scope.enddate;
          if (startdate) {
                if (enddate) {      
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&max_birth_date=" + enddate )
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                } else {
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                }
          } else {
              if (enddate) {
                $http.get("/kiramama/reportnsc/?max_birth_date=" + enddate )
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
              }
          }
      };
  }]);
