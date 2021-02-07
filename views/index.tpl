<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">

    <title>Cizi problem</title>
  </head>
  <body>
    <h1 class="col-lg-6 offset-lg-3">{{name}}</h1>
    <form id="formTemplate" class="col-lg-6 offset-lg-3">
      {% for key, value in context.items() %}
      <div class="form-group row">
        <label for="input{{ key }}" class="col-sm-6 col-form-label">{{ key }}</label>
        <div class="col-sm-6">
          <input type="text" class="form-control" id="input{{ key }}" name="{{ key }}" placeholder="{{value}}">
        </div>
      </div>
      {% endfor %}
      <div class="form-group row">
        <div class="col-sm-6">
          <button type="submit" class="btn btn-primary">Generate</button>
        </div>
      </div>
    </form>
    <script>
      var saveData = (function () {
        var a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        return function (blob, fileName) {
          url = window.URL.createObjectURL(blob);
          a.href = url;
          a.download = fileName;
          a.click();
          window.URL.revokeObjectURL(url);
        };
      }());

      formTemplate.onsubmit = async (e) => {
        e.preventDefault();
        const form = new FormData(document.getElementById('formTemplate'));
        let response = await fetch('/generate', { method: 'POST', body: form });
        let result = await response.blob();
        saveData(result, '{{ name }}.docx');

      };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js" integrity="sha384-ygbV9kiqUc6oa4msXn9868pTtWMgiQaeYH7/t7LECLbyPA2x65Kgf80OJFdroafW" crossorigin="anonymous"></script>

  </body>
</html>
