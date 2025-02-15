from flask import Flask, request, render_template_string
import pdfplumber

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Upload Wolt KM Rapport</title>
    <style>
        /* Reset básico */
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        body {
          background-color: #e0f7fa; /* fondo celeste claro */
          color: #01579b; /* texto en azul oscuro */
          font-family: Arial, sans-serif;
          line-height: 1.6;
          padding: 20px;
        }
        .container {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
          background: #ffffff;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1, h2 {
          text-align: center;
          margin-bottom: 20px;
        }
        form {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        input[type="file"] {
          margin-bottom: 15px;
        }
        input[type="submit"] {
          background-color: #4fc3f7;
          color: #ffffff;
          border: none;
          padding: 10px 20px;
          font-size: 16px;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
          background-color: #0288d1;
        }
        .result {
          margin-top: 20px;
          text-align: center;
        }
        .error {
          margin-top: 20px;
          text-align: center;
          color: red;
        }
        a {
          text-decoration: none;
          color: #0288d1;
        }
        a:hover {
          text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        {% if result %}
            <h2>Result:</h2>
            <p>Total km: {{ total_km }} km</p>
            <p>Total km deducible: {{ km_deducible }} km</p>
            <p>Total deducible en coronas: {{ deducible_dkk }} DKK</p>
            <br>
            <div style="text-align:center;">
                <a href="/">Subir otro archivo</a>
            </div>
        {% else %}
            <h1>Upload Wolt KM Rapport</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="application/pdf">
                <input type="submit" value="Process">
            </form>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verifica si se subió un archivo
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, error="No se subió ningún archivo.", result=False)
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, error="El archivo no tiene nombre.", result=False)
        
        try:
            with pdfplumber.open(file) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    extracted = pagina.extract_text()
                    if extracted:
                        texto_completo += extracted

            # Divide el texto en líneas
            lineas = texto_completo.split('\n')

            # Procesamos el texto para extraer la columna de kilómetros
            datos_km = []
            for linea in lineas:
                if not linea.strip():
                    continue
                partes = linea.split()
                if len(partes) >= 3 and partes[2].replace('.', '', 1).isdigit():
                    datos_km.append(partes[2])

            # Convertir los kilómetros a flotantes
            datos_km = [float(km) for km in datos_km]

            km_deducible = 0
            dias_over24 = 0
            for km in datos_km:
                if km > 24:
                    km_deducible += km
                    dias_over24 += 1

            total_km = sum(datos_km)
            km_no_deducibles = dias_over24 * 24
            km_deducible = km_deducible - km_no_deducibles
            deducible_dkk = km_deducible * 2.23

            return render_template_string(HTML_TEMPLATE,
                                          result=True,
                                          total_km=round(total_km, 2),
                                          km_deducible=round(km_deducible, 2),
                                          deducible_dkk=round(deducible_dkk, 2),
                                          error=None)
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=f"Error procesando el archivo: {str(e)}", result=False)
    
    # Si es GET, mostramos el formulario (último return)
    return render_template_string(HTML_TEMPLATE, result=False, error=None)

if __name__ == '__main__':
    app.run(debug=True)