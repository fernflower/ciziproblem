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

    <title>Cizi problem</title>

    <style type="text/css">
      body {
        padding: 20px 0;
      }
    </style>
  </head>
  <body class='bg-light'>
    <div class='container'>
      <div class="image"></div>
      <h2>Which document do you want to create today?</h2>
      <div class="options">
        {% for group in documents %}
        <div class="row row-cols-1 row-cols-md-2 g-4 mt-1">
          {% for doc in group %}
          <div class="col">
            <div class="card border-{{ doc.get('css_style', 'info') }}">
              <div class="card-header">{{ doc.get('header') }}</div>
              <div class="card-body">
              {%- for elem in doc.get('body') %}
                {%- if elem.get('type') == 'list' %}
                  <ul class="list-group">
                    {% for li in elem.get('value') %}
                      <li class="list-group-item">{{ li }}</li>
                    {% endfor %}
                {% else %}
                  <p class="card-text">{{ elem.get('value') }}</p>
                {% endif %}
              {%- endfor %}
              <div class="card-footer text-end">
                <a href="{{ doc.get('link') }}" class="btn btn-{{ doc.get('css_style', 'info') }}"><i class="bi bi-arrow-right"></i></a>
              </div>
            </div> <!-- card-body -->
          </div> <!-- card -->
          </div> <!-- col -->
          {% endfor %}
        </div>
        {% endfor %}
      </div>
    </div>

    <div class="col-xs-1 text-center pt-5">
      <p class="text-muted small">Created by <a href="https://github.com/fernflower">fernflower</a>, 2021</p>
    </div>
  </body>
</html>
