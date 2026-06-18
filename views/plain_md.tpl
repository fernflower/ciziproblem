<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">

    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>

    <style type="text/css">
      body {
        padding: 20px 0;
      }
      .content-card {
        margin-top: 1.5rem;
        padding: 2rem;
        background: #fff;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
      }
    </style>

    <title>Cizi problem</title>
  </head>
  <body class="bg-light">
    <div class="container">
      <main>
        <div class="row g-3">
          <a href="/" class="btn btn-outline-primary">Go back</a>
        </div>

        <div class="content-card">
            {{ content }}
        </div>
      </main>
    </div>
    <div class="col-xs-1 text-center pt-5">
      <p class="text-muted small">Created by <a href="https://github.com/fernflower">fernflower</a>, 2026</p>
    </div>
  </body>

</html>
