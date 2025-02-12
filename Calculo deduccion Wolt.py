from flask import Flask, request, render_template_string
import pdfplumber

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verifica si se subió un archivo
        if 'file' not in request.files:
            return "No se subió ningún archivo."

        file = request.files['file']
        if file.filename == '':
            return "El archivo no tiene nombre."

        # Abrimos el archivo PDF subido
        try:
            with pdfplumber.open(file) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto_completo += pagina.extract_text()

            # Divide el texto en líneas
            lineas = texto_completo.split('\n')

            # Procesamos el texto para extraer la columna de kilómetros
            datos_km = []  # Lista para guardar los kilómetros
            for linea in lineas:
                if not linea.strip():  # Ignorar líneas vacías
                    continue

                # Dividir la línea en partes
                partes = linea.split()

                # Validar que tiene al menos 3 columnas y que la tercera columna es un número
                if len(partes) >= 3 and partes[2].replace('.', '', 1).isdigit():
                    km = partes[2]  # Extraer kilómetros
                    datos_km.append(km)

            # Convertir los kilómetros a flotantes
            datos_km = [float(km) for km in datos_km]

            # Generamos el resultado como HTML
            resultado_html = "<h2>Resultados:</h2><ul>"
            km_deducible=0
            dias_over24=0
            for km in datos_km:
                if km>24:
                    km_deducible+=km
                    dias_over24+=1
            total_km=sum(datos_km)
            km_no_deducibles=dias_over24*24
            km_deducible=km_deducible-km_no_deducibles
            deducible_dkk=km_deducible*2.23
            resultado_html = f"""
                <h2>Result:</h2>
                Total km: {round(total_km, 2)} km<br>
                Total km deducible: {round(km_deducible, 2)} km<br>
                Total deducible en coronas: {round(deducible_dkk,2)} DKK
            """
            return resultado_html

        except Exception as e:
            return f"Error procesando el archivo: {str(e)}"

    # Si es GET, mostramos el formulario
    return '''
        <!doctype html>
        <title>Upload wolt km rapport</title>
        <h1>Upload wolt km rapport</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="application/pdf">
            <input type="submit" value="Process">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)