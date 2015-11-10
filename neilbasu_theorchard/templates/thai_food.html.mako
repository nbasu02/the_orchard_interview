<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Finding Thai food">
    <meta name="author" content="Neil Basu">

    <title>Thai food!</title>

    <!-- Bootstrap core CSS -->
    <link href="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this scaffold -->
    <link href="${request.static_url('neilbasu_theorchard:static/theme.css')}" rel="stylesheet">

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
    <script src="https://maps.googleapis.com/maps/api/js"></script>
    <script src="static/restaurant_maps.js"></script>
    <script type="text/javascript">
      document.addEventListener("DOMContentLoaded", function(event) {
        var map = initMap();
        var addresses = [];
        % for restaurant in restaurants:
          addresses.push('${restaurant.address}');
        % endfor
        addMarkers(addresses, map);
      });
    </script>
  </head>

  <body>

  <h1>Looking for good Thai?  Check out:</h1>
    <div >
      <div id="map" style="width:500px; height:300px"></div>
      <div class="col-md-10">
        % for restaurant in restaurants:
        <div class="content">
          <h2>${restaurant.name}</h2>
          <p class="lead font-normal">Grade: ${restaurant.grade}<br/>
          Rated: ${int(restaurant.numeric_grade)}/5<br/>
          Address: ${restaurant.address}
          </p>
        </div>
        % endfor
      </div>
    </div>
  </body>
</html>
