# Importamos los módulos necesarios de Flask
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy  # Extensión para trabajar con bases de datos SQL en Flask
import os  # Módulo para interactuar con el sistema de archivos
from flask import Flask, session, flash  # `session` permite almacenar datos de usuario en la sesión

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de una clave secreta para la aplicación.
# Esta clave se usa para manejar sesiones y mensajes flash de manera segura.
app.secret_key = "clave_super_segura"

# ⚠️ Aquí hay un error: Se está volviendo a definir `app`, sobrescribiendo la configuración anterior.
app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumnos.db'  # Definimos la base de datos SQLite
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Carpeta donde se almacenarán los archivos subidos

# Creamos una instancia de SQLAlchemy para gestionar la base de datos
db = SQLAlchemy(app)

# Definimos un modelo llamado 'Alumno' que representa una tabla en la base de datos.
class Alumno(db.Model):
    # Columna 'id' de tipo entero, es la clave primaria de la tabla (identificador único).
    id = db.Column(db.Integer, primary_key=True)
    
    # Columna 'nombre' de tipo cadena con un máximo de 100 caracteres. No puede ser nula.
    nombre = db.Column(db.String(100), nullable=False)

    # Columna 'dni' de tipo cadena con un máximo de 10 caracteres.
    # Se define como única (`unique=True`) para evitar duplicados y no puede ser nula.
    dni = db.Column(db.String(10), unique=True, nullable=False)

    # Columna 'email' de tipo cadena con un máximo de 100 caracteres.
    # También debe ser único para evitar que se registren correos duplicados.
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Columna 'domicilio' de tipo cadena con un máximo de 200 caracteres.
    # Es obligatoria (`nullable=False`).
    domicilio = db.Column(db.String(200), nullable=False)

    # Columna 'foto' de tipo cadena con un máximo de 200 caracteres.
    # Puede ser nula (`nullable=True`), lo que indica que un alumno puede no tener foto.
    foto = db.Column(db.String(200), nullable=True)


@app.route('/')  # Es un decorador de Flask que asocia la función index() con la URL raíz (/).
#Cuando un usuario accede a la página principal, Flask ejecuta esta función.
def index(): #Define la función index() que manejará la solicitud cuando un usuario acceda a la ruta /.
    # Consulta la base de datos y obtiene todos los registros de la tabla 'Alumno'.
    # 'Alumno.query.all()' devuelve una lista de objetos Alumno con todos los alumnos almacenados.
    alumnos = Alumno.query.all()  
    
    # Renderiza la plantilla 'index.html' y le pasa la lista de alumnos obtenida.
    # En 'index.html', se podrá recorrer la lista 'alumnos' y mostrar la información en una tabla u otro formato.
    return render_template('index.html', alumnos=alumnos)


@app.route('/agregar', methods=['GET', 'POST'])  
# Es un decorador de Flask que define la ruta '/agregar'.
# Permite manejar solicitudes GET y POST.
# - GET: Muestra el formulario para agregar un nuevo alumno.
# - POST: Recibe los datos del formulario y los guarda en la base de datos.
def agregar():  
    if request.method == 'POST':  # Verifica si la solicitud es de tipo POST.
        
        # Obtiene los datos enviados desde el formulario a través de request.form.
        nombre = request.form['nombre']  # Captura el valor del campo 'nombre'.
        dni = request.form['dni']  # Captura el valor del campo 'dni'.
        email = request.form['email']  # Captura el valor del campo 'email'.
        domicilio = request.form['domicilio']  # Captura el valor del campo 'domicilio'.
        foto = request.files['foto']  # Captura el archivo de imagen enviado en el campo 'foto'.

        if foto:  # Verifica si se subió una foto.
            # Genera la ruta donde se almacenará la imagen dentro de la carpeta configurada en 'UPLOAD_FOLDER'.
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)  # Guarda la imagen en la ruta especificada.
        else:
            foto_path = None  # Si no se subió una foto, se almacena como None.

        # Crea un nuevo objeto Alumno con los datos recibidos.
        nuevo_alumno = Alumno(nombre=nombre, dni=dni, email=email, domicilio=domicilio, foto=foto_path)

        # Agrega el nuevo alumno a la sesión de la base de datos.
        db.session.add(nuevo_alumno)

        # Guarda los cambios en la base de datos de manera permanente.
        db.session.commit()

        # Redirige al usuario a la página principal después de agregar el alumno.
        return redirect(url_for('index'))

    # Si la solicitud es GET, renderiza la plantilla 'agregar.html' para mostrar el formulario.
    return render_template('agregar.html')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])  
# Es un decorador de Flask que define la ruta '/editar/<id>'.
# <int:id> indica que la URL debe contener un número entero (ID del alumno).
# Permite manejar solicitudes GET y POST.
# - GET: Muestra el formulario con los datos actuales del alumno.
# - POST: Recibe los datos editados y actualiza el alumno en la base de datos.
def editar(id):  
    # Obtiene el objeto Alumno con el ID proporcionado.
    # Si el alumno no existe, devuelve un error 404.
    alumno = Alumno.query.get_or_404(id)

    if request.method == 'POST':  # Verifica si la solicitud es de tipo POST.
        # Captura los nuevos valores del formulario y los asigna al objeto 'alumno'.
        alumno.nombre = request.form['nombre']
        alumno.dni = request.form['dni']
        alumno.email = request.form['email']
        alumno.domicilio = request.form['domicilio']

        # Captura el archivo de imagen si el usuario subió una nueva foto.
        foto = request.files['foto']
        if foto:  # Si se subió una nueva foto:
            # Genera la ruta donde se almacenará la imagen dentro de la carpeta configurada en 'UPLOAD_FOLDER'.
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)  # Guarda la imagen en la ruta especificada.

            # Actualiza la foto del alumno con la nueva imagen.
            alumno.foto = foto_path

        # Guarda los cambios en la base de datos.
        db.session.commit()

        # Redirige al usuario a la página principal después de la edición.
        return redirect(url_for('index'))

    # Si la solicitud es GET, renderiza la plantilla 'editar.html' y le pasa el objeto 'alumno'.
    # Esto permite mostrar los datos actuales en el formulario para que el usuario los edite.
    return render_template('editar.html', alumno=alumno)


@app.route('/eliminar/<int:id>')  
# Este decorador de Flask define la ruta '/eliminar/<id>', donde <id> es un parámetro entero.
# La ruta elimina el alumno correspondiente al ID proporcionado en la URL.

def eliminar(id):  
    # Se obtiene el objeto 'alumno' a partir del ID proporcionado en la URL.
    # Si no se encuentra el alumno con ese ID, se lanza un error 404.
    alumno = Alumno.query.get_or_404(id)

    # Se elimina el objeto 'alumno' de la base de datos.
    db.session.delete(alumno)

    # Se confirma la eliminación en la base de datos.
    db.session.commit()

    # Después de eliminar el alumno, se redirige al usuario a la página principal (index).
    return redirect(url_for('index'))



class Nota(db.Model):  
    # Define la clase 'Nota', que representa la tabla 'nota' en la base de datos.
    # 'Nota' tiene los siguientes atributos:
    
    id = db.Column(db.Integer, primary_key=True)  
    # 'id' es una columna de tipo entero que actúa como la clave primaria de la tabla.
    # Esta columna es única para cada registro de nota y se genera automáticamente.

    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)  
    # 'alumno_id' es una columna que guarda el ID del alumno relacionado con esta nota.
    # Es una clave foránea que referencia el campo 'id' de la tabla 'alumno'.
    # La propiedad 'nullable=False' asegura que este campo no pueda estar vacío.

    materia = db.Column(db.String(100), nullable=False)  
    # 'materia' es una columna que almacena el nombre de la materia en la que se ha asignado la nota.
    # El campo es de tipo cadena (string) y tiene un máximo de 100 caracteres.
    # La propiedad 'nullable=False' asegura que este campo debe ser proporcionado al crear una nota.

    nota = db.Column(db.Float, nullable=False)  
    # 'nota' es una columna de tipo flotante que almacena el valor numérico de la nota del alumno en esa materia.
    # La propiedad 'nullable=False' asegura que este campo no pueda estar vacío al guardar una nota.


@app.route('/cargar_notas', methods=['GET', 'POST'])  
# El decorador @app.route('/cargar_notas') asigna la función 'cargar_notas' a la ruta '/cargar_notas' de la aplicación.
# Esta ruta manejará las solicitudes tanto GET como POST.
def cargar_notas():
    if request.method == 'POST':  
        # Si el método de la solicitud es POST, significa que el formulario ha sido enviado.
        
        dni = request.form['dni']  
        # Recupera el DNI del alumno desde el formulario (campo 'dni').
        print(f"DNI ingresado: {dni}")  # Imprime el DNI en la consola para verificar que se está enviando correctamente.
        
        alumno = Alumno.query.filter_by(dni=dni).first()  
        # Realiza una consulta a la base de datos para buscar un alumno cuyo DNI coincida con el proporcionado.
        # 'filter_by' busca el primer registro que coincida con el valor de 'dni'.
        print(f"Alumno encontrado: {alumno}")  # Imprime el objeto 'alumno' encontrado para depuración.
        
        if not alumno:  
            # Si no se encuentra un alumno con el DNI proporcionado, se retorna un error 404 con un mensaje.
            return "Alumno no encontrado", 404
        
        # Lista de materias que se utilizan para cargar las notas.
        materias = ["Matemática", "Lengua", "Historia", "Geografía", "Biología", "Física", "Química", "Inglés", "Arte", "Educación Física"]
        
        notas = []  # Lista que almacenará las notas de las materias.
        
        for materia in materias:  
            # Itera sobre la lista de materias.
            
            # Obtiene el valor de la nota de cada materia del formulario (campo con nombre igual a la materia).
            nota_valor = request.form.get(materia)
            
            if nota_valor:  # Si se proporciona una nota para la materia, se crea una nueva instancia de 'Nota'.
                # Crea un objeto 'Nota' con el ID del alumno, la materia y la nota proporcionada en el formulario.
                nota = Nota(alumno_id=alumno.id, materia=materia, nota=float(nota_valor))
                
                # Agrega la nueva nota a la base de datos.
                db.session.add(nota)
                
                # Agrega el valor de la nota a la lista 'notas' para calcular el promedio después.
                notas.append(float(nota_valor))
        
        db.session.commit()  
        # Realiza la confirmación (commit) de las modificaciones en la base de datos (se guardan las notas).

        promedio = sum(notas) / len(notas) if notas else 0  
        # Calcula el promedio de las notas.
        # Si la lista de notas no está vacía, se suman las notas y se dividen por la cantidad de notas.
        # Si no se proporcionaron notas, el promedio es 0.
        
        return render_template('cargar_notas.html', alumno=alumno, materias=materias, promedio=promedio)
        # Renderiza la plantilla 'cargar_notas.html' y pasa los datos del alumno, las materias y el promedio calculado.
    
    return render_template('cargar_notas.html', materias=["Matemática", "Lengua", "Historia", "Geografía", "Biología", "Física", "Química", "Inglés", "Arte", "Educación Física"])
    # Si la solicitud es GET (cuando se accede a la página inicialmente), renderiza la plantilla 'cargar_notas.html'
    # solo con la lista de materias, sin mostrar información de notas o promedios.

@app.route('/buscar_alumno', methods=['POST'])  
# El decorador @app.route('/buscar_alumno', methods=['POST']) asigna la función 'buscar_alumno' a la ruta '/buscar_alumno'.
# Esta ruta maneja únicamente solicitudes POST (generalmente utilizadas cuando los datos se envían desde un formulario o solicitud AJAX).
def buscar_alumno():
    dni = request.form.get('dni')  
    # Captura el valor del campo 'dni' enviado a través de la solicitud POST (posiblemente un formulario o solicitud AJAX).
    # Se utiliza request.form.get() para obtener el valor de 'dni' del formulario.
    
    alumno = Alumno.query.filter_by(dni=dni).first()  
    # Realiza una consulta a la base de datos para buscar un alumno que tenga el DNI proporcionado.
    # 'filter_by(dni=dni)' filtra los registros de la tabla Alumno para encontrar uno con el DNI que coincida con el valor enviado.
    # 'first()' devuelve el primer resultado encontrado o None si no se encuentra un alumno con ese DNI.
    
    if alumno:  
        # Si se encuentra un alumno con el DNI proporcionado, se devuelve una respuesta en formato JSON con los datos del alumno.
        return jsonify({
            "nombre": alumno.nombre,  # El nombre del alumno.
            "email": alumno.email,    # El correo electrónico del alumno.
            "domicilio": alumno.domicilio,  # El domicilio del alumno.
            "foto": alumno.foto  # La ruta de la foto del alumno.
        })
    
    # Si no se encuentra el alumno, se devuelve una respuesta JSON con un mensaje de error y el código de estado 404.
    return jsonify({"error": "Alumno no encontrado"}), 404  
    # 'jsonify()' convierte el diccionario en una respuesta JSON que se enviará al cliente.
    # El código 404 indica que no se encontró al alumno.


@app.route('/mostrar_notas')  
# El decorador @app.route('/mostrar_notas') asigna la función 'mostrar_notas' a la ruta '/mostrar_notas'.
# Esta ruta maneja solicitudes GET y se utiliza para mostrar las notas de todos los alumnos.

def mostrar_notas():
    alumnos = Alumno.query.all()  
    # Se consulta la base de datos para obtener todos los registros de la tabla 'Alumno'.
    # Esto devuelve una lista con todos los alumnos registrados en la base de datos.

    datos_alumnos = []  
    # Se inicializa una lista vacía que almacenará los datos de cada alumno junto con sus notas y su promedio.

    for alumno in alumnos:  
        # Se itera sobre cada alumno obtenido de la base de datos.
        
        notas = Nota.query.filter_by(alumno_id=alumno.id).all()  
        # Para cada alumno, se realiza una consulta a la tabla 'Nota' para obtener todas las notas asociadas a ese alumno.
        # 'alumno_id=alumno.id' filtra las notas que corresponden a este alumno específico.

        if notas:  
            # Si el alumno tiene notas registradas...
            promedio = sum(n.nota for n in notas) / len(notas)  
            # Se calcula el promedio de las notas del alumno.
            # 'sum(n.nota for n in notas)' obtiene la suma de todas las notas.
            # 'len(notas)' devuelve la cantidad de notas para calcular el promedio.
        else:  
            # Si el alumno no tiene notas registradas...
            promedio = 0  # Si no tiene notas, el promedio se establece en 0.

        # Se agrega un diccionario con los datos del alumno, sus notas y su promedio calculado a la lista 'datos_alumnos'.
        datos_alumnos.append({
            "alumno": alumno,  # Los datos del alumno (objeto Alumno).
            "notas": notas,  # Las notas del alumno (lista de objetos Nota).
            "promedio": round(promedio, 2)  # El promedio de las notas, redondeado a dos decimales.
        })

    return render_template('mostrar_notas.html', datos_alumnos=datos_alumnos)  
    # Se renderiza la plantilla 'mostrar_notas.html', pasando la lista 'datos_alumnos' a la plantilla.
    # En 'mostrar_notas.html', se podrá acceder a la lista 'datos_alumnos' para mostrar los datos de cada alumno,
    # sus notas y su promedio de manera dinámica.


@app.route('/editar_nota/<int:id>', methods=['GET', 'POST'])
# Este decorador @app.route asocia la función 'editar_nota' a la URL '/editar_nota/<int:id>'.
# El parámetro <int:id> captura el ID de la nota que se quiere editar.
# El método 'GET' se usa para mostrar el formulario de edición y el método 'POST' para procesar los datos enviados.

def editar_nota(id):
    # 'Nota.query.get_or_404(id)' busca la nota con el ID proporcionado.
    # Si la nota no existe, se genera un error 404 (página no encontrada).
    nota = Nota.query.get_or_404(id)
    
    if request.method == 'POST':
        # Si el método es 'POST', significa que el formulario de edición fue enviado.
        
        nueva_nota = request.form['nota']  # Obtiene la nueva nota del formulario.
        nota.nota = float(nueva_nota)  # Actualiza el campo 'nota' de la base de datos con el nuevo valor.
        
        # Se guarda la actualización en la base de datos.
        db.session.commit()
        
        # Se redirige a la ruta 'mostrar_notas' para mostrar las notas actualizadas.
        return redirect(url_for('mostrar_notas'))

    # Si el método es 'GET', se renderiza el formulario de edición.
    # Se pasa la nota a la plantilla 'editar_nota.html' para que el usuario pueda ver y editar su valor.
    return render_template('editar_nota.html', nota=nota)


@app.route('/eliminar_nota/<int:id>')
# Este decorador @app.route asocia la función 'eliminar_nota' a la URL '/eliminar_nota/<int:id>'.
# Captura el ID de la nota que se desea eliminar.

def eliminar_nota(id):
    # 'Nota.query.get_or_404(id)' busca la nota con el ID proporcionado.
    # Si no la encuentra, genera un error 404.
    nota = Nota.query.get_or_404(id)
    
    # Elimina la nota de la base de datos.
    db.session.delete(nota)
    # Guarda la eliminación en la base de datos.
    db.session.commit()
    
    # Después de eliminar la nota, redirige a la ruta 'mostrar_notas' para mostrar la lista de notas actualizada.
    return redirect(url_for('mostrar_notas'))


if __name__ == '__main__':
    # Este bloque asegura que si la carpeta 'static/uploads' no existe, se cree.
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')

    # Este bloque crea todas las tablas de la base de datos si no existen.
    with app.app_context():
        db.create_all()

    # Arranca el servidor Flask en modo de depuración (debug).
    app.run(debug=True)

