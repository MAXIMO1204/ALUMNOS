from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, session, flash

app = Flask(__name__)
app.secret_key = "clave_super_segura"



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumnos.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)

class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    domicilio = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(200), nullable=True)

@app.route('/')
def index():
    alumnos = Alumno.query.all()
    return render_template('index.html', alumnos=alumnos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        email = request.form['email']
        domicilio = request.form['domicilio']
        foto = request.files['foto']

        if foto:
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)
        else:
            foto_path = None

        nuevo_alumno = Alumno(nombre=nombre, dni=dni, email=email, domicilio=domicilio, foto=foto_path)
        db.session.add(nuevo_alumno)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('agregar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    alumno = Alumno.query.get_or_404(id)
    if request.method == 'POST':
        alumno.nombre = request.form['nombre']
        alumno.dni = request.form['dni']
        alumno.email = request.form['email']
        alumno.domicilio = request.form['domicilio']

        foto = request.files['foto']
        if foto:
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)
            alumno.foto = foto_path

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('editar.html', alumno=alumno)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    alumno = Alumno.query.get_or_404(id)
    db.session.delete(alumno)
    db.session.commit()
    return redirect(url_for('index'))



class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    materia = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False)

@app.route('/cargar_notas', methods=['GET', 'POST'])
def cargar_notas():
    if request.method == 'POST':
        dni = request.form['dni']
        print(f"DNI ingresado: {dni}")  # Verifica que el DNI se está enviando correctamente
        
        alumno = Alumno.query.filter_by(dni=dni).first()
        print(f"Alumno encontrado: {alumno}")  # Verifica qué devuelve la consulta
        
        if not alumno:
            return "Alumno no encontrado", 404
        
        materias = ["Matemática", "Lengua", "Historia", "Geografía", "Biología", "Física", "Química", "Inglés", "Arte", "Educación Física"]
        
        notas = []
        for materia in materias:
            nota_valor = request.form.get(materia)
            if nota_valor:
                nota = Nota(alumno_id=alumno.id, materia=materia, nota=float(nota_valor))
                db.session.add(nota)
                notas.append(float(nota_valor))
        
        db.session.commit()
        promedio = sum(notas) / len(notas)
        
        return render_template('cargar_notas.html', alumno=alumno, materias=materias, promedio=promedio)
    
    return render_template('cargar_notas.html', materias=["Matemática", "Lengua", "Historia", "Geografía", "Biología", "Física", "Química", "Inglés", "Arte", "Educación Física"])

@app.route('/buscar_alumno', methods=['POST'])
def buscar_alumno():
    dni = request.form.get('dni')  # Captura el DNI enviado por AJAX
    alumno = Alumno.query.filter_by(dni=dni).first()
    
    if alumno:
        return jsonify({
            "nombre": alumno.nombre,
            "email": alumno.email,
            "domicilio": alumno.domicilio,
            "foto": alumno.foto
        })
    
    return jsonify({"error": "Alumno no encontrado"}), 404


@app.route('/mostrar_notas')
def mostrar_notas():
    alumnos = Alumno.query.all()
    datos_alumnos = []

    for alumno in alumnos:
        notas = Nota.query.filter_by(alumno_id=alumno.id).all()
        if notas:
            promedio = sum(n.nota for n in notas) / len(notas)
        else:
            promedio = 0  # Si no tiene notas, el promedio es 0

        datos_alumnos.append({
            "alumno": alumno,
            "notas": notas,
            "promedio": round(promedio, 2)
        })

    return render_template('mostrar_notas.html', datos_alumnos=datos_alumnos)

@app.route('/editar_nota/<int:id>', methods=['GET', 'POST'])
def editar_nota(id):
    nota = Nota.query.get_or_404(id)
    
    if request.method == 'POST':
        nueva_nota = request.form['nota']
        nota.nota = float(nueva_nota)
        db.session.commit()
        return redirect(url_for('mostrar_notas'))

    return render_template('editar_nota.html', nota=nota)

@app.route('/eliminar_nota/<int:id>')
def eliminar_nota(id):
    nota = Nota.query.get_or_404(id)
    db.session.delete(nota)
    db.session.commit()
    return redirect(url_for('mostrar_notas'))


if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    
    with app.app_context():
        db.create_all()

    app.run(debug=True)
