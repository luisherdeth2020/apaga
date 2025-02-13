from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def resaltar_diferencias(row):
    if row['diferencia'] == 'Solo en dia7.csv':
        return f'<span style="color: green">{row["email_dia7"]}</span>'
    elif row['diferencia'] == 'Solo en bobo.csv':
        return f'<span style="color: green">{row["email_bobo"]}</span>'
    elif row['diferencia'] == 'Información distinta':
        tmp_diff = []
        if row['name_dia7'] != row['name_bobo']:
            tmp_diff.append(f'Nombre: <span style="color: red">{row["name_bobo"]}</span>')
        if row['email_dia7'] != row['email_bobo']:
            tmp_diff.append(f'Email: <span style="color: red">{row["email_bobo"]}</span>')
        return ' | '.join(tmp_diff) if tmp_diff else row['email_dia7']
    return row['email_dia7']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded files
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and file2:
            # Save the files temporarily in the uploads folder
            path1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            path2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
            file1.save(path1)
            file2.save(path2)
            
            # Load CSV files
            df1 = pd.read_csv(path1)
            df2 = pd.read_csv(path2)
            
            # Add an original order column
            df1['orden_original'] = range(len(df1))
            df2['orden_original'] = range(len(df2))
            
            diferencias = []
            
            for i in range(max(len(df1), len(df2))):
                if i >= len(df1):
                    diferencias.append({
                        'fila': i + 1,
                        'name_dia7': None,
                        'email_dia7': None,
                        'name_bobo': df2.loc[i, 'name'],
                        'email_bobo': df2.loc[i, 'email'],
                        'diferencia': 'Solo en bobo.csv'
                    })
                elif i >= len(df2):
                    diferencias.append({
                        'fila': i + 1,
                        'name_dia7': df1.loc[i, 'name'],
                        'email_dia7': df1.loc[i, 'email'],
                        'name_bobo': None,
                        'email_bobo': None,
                        'diferencia': 'Solo en dia7.csv'
                    })
                else:
                    name_dia7 = df1.loc[i, 'name']
                    email_dia7 = df1.loc[i, 'email']
                    name_bobo = df2.loc[i, 'name']
                    email_bobo = df2.loc[i, 'email']
                    
                    if name_dia7 == name_bobo and email_dia7 == email_bobo:
                        continue
                    
                    diferencias.append({
                        'fila': i + 1,
                        'name_dia7': name_dia7,
                        'email_dia7': email_dia7,
                        'name_bobo': name_bobo,
                        'email_bobo': email_bobo,
                        'diferencia': 'Información distinta'
                    })
            
            # Convert list of dictionaries to DataFrame
            df_resultado = pd.DataFrame(diferencias)
            df_resultado['email_formateado'] = df_resultado.apply(resaltar_diferencias, axis=1)
            
            # Save results globally (for example purposes only)
            global resultados
            resultados = df_resultado.to_dict(orient='records')
            return redirect(url_for('index'))
        
        # If files are missing, you might handle the error here
        return render_template('index.html', resultado=resultados if 'resultados' in globals() else None)
    
    # GET: Render the template with results if available
    return render_template('index.html', resultado=resultados if 'resultados' in globals() else None)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

if __name__ == '__main__':
    app.run(debug=True)