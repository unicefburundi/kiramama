var app = angular.module('ChildApp', ['ngSanitize', 'datatables', 'datatables.buttons']);

app.controller('ChildCtrl', ['$scope', '$http', 'DTOptionsBuilder', function($scope, $http, DTOptionsBuilder) {
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
            $scope.districts = "";
            $scope.cdss = "";
            $scope.startdate = "";
            $scope.enddate = "";
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
            $scope.cdss = "";
            $scope.startdate = "";
            $scope.enddate = "";
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
            $scope.startdate = "";
            $scope.enddate = "";
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
          var cds = $scope.cds;
          var district = $scope.district;
          var province = $scope.province;
          if (startdate && cds) {
                if (enddate) {      
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&max_birth_date=" + enddate + "&cds=" + cds.code)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                } else {
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&cds=" + cds.code)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                }
          } else if (startdate && district) {
                    if (enddate) {      
                        $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&max_birth_date=" + enddate + "&district=" + district.code)
                          .then(function (response) {
                              $scope.results = response.data.results;
                          });
                    } else {
                        $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&district=" + district.code)
                          .then(function (response) {
                              $scope.results = response.data.results;
                          });
                    }
              } else if (startdate && province) {
                if (enddate) {      
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&max_birth_date=" + enddate + "&province=" + province.code)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                } else {
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&province=" + province.code)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                }
          } else if (startdate) {
                if (enddate) {      
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate + "&max_birth_date=" + enddate)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                } else {
                    $http.get("/kiramama/reportnsc/?min_birth_date=" + startdate)
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                }
          } else if (enddate) {
                $http.get("/kiramama/reportnsc/?max_birth_date=" + enddate )
                      .then(function (response) {
                          $scope.results = response.data.results;
                      });
                }
      };
      // for datatable 

      $scope.dtOptions = DTOptionsBuilder.newOptions().withPaginationType('full_numbers').withButtons([ 'copy', 'csv', 'excel', 'pdf', 'print']).withDOM("<'row'<'col-sm-3'l><'col-sm-4'i><'col-sm-5'f>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-4'B><'col-sm-8'p>>").withDisplayLength(10);
  }]);
