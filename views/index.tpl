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
      .card-columns {
        column-count: 1;
        column-gap: 1.5rem;
      }
      @media (min-width: 768px) {
        .card-columns {
          column-count: 2;
        }
      }
      .card-columns .card {
        break-inside: avoid;
        margin-bottom: 1.5rem;
      }
    </style>
  </head>
  <body class='bg-light'>
    <div class='container'>
      <div class="image"></div>
      <h2>What problem are you facing today?</h2>
      <div class="options">
        {% for group in documents %}
        <div class="card-columns mt-3">
          {% for doc in group %}
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
          {% endfor %}
        </div>
        {% endfor %}
      </div>
    </div>

    <div class="col-xs-1 text-center pt-5">
      <p class="text-muted small">Created by <a href="https://github.com/fernflower">fernflower</a>, 2026</p>
    </div>
  </body>
</html>
