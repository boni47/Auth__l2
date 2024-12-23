from falsk import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import random
import string

app = Flask(__name__)

# Конфигурация для SQLAlchemy и JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Для JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # Время жизни токена (1 час)

# Инициализация расширений
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    nickname = db.Column(db.String(150), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Создание базы данных
with app.app_context():
    db.create_all()

# Генерация случайного пароля длиной 16 символов
def generate_random_password():
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for i in range(16))
    return password

# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')
    email = data.get('email')
    phone = data.get('phone')
    nickname = data.get('nickname')
    gender = data.get('gender')
    avatar_url = data.get('avatarUrl')

    # Проверка совпадения паролей
    if password != confirm_password:
        return jsonify({"message": "Пароли не совпадают"}), 400

    # Проверка на пробелы в полях
    if ' ' in username or ' ' in password:
        return jsonify({"message": "Поля не могут содержать пробелы"}), 400

    # Хэширование пароля
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Создание нового пользователя
    new_user = User(
        username=username,
        password=hashed_password,
        email=email,
        phone=phone,
        nickname=nickname,
        gender=gender,
        avatar_url=avatar_url
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Регистрация успешна"}), 201

# Вход пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        # Генерация JWT токена
        access_token = create_access_token(identity={'id': user.id, 'username': user.username})
        return jsonify({"token": access_token}), 200
    return jsonify({"message": "Неверный логин или пароль"}), 400

# Получение данных пользователя
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    if user:
        return jsonify({
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'nickname': user.nickname,
            'gender': user.gender,
            'avatar_url': user.avatar_url,
            'created_at': user.created_at
        })
    return jsonify({"message": "Пользователь не найден"}), 404

# Изменение данных пользователя
@app.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    if not user:
        return jsonify({"message": "Пользователь не найден"}), 404

    data = request.get_json()

    # Обновляем данные пользователя
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.nickname = data.get('nickname', user.nickname)
    user.gender = data.get('gender', user.gender)
    user.avatar_url = data.get('avatarUrl', user.avatar_url)

    db.session.commit()

    return jsonify({"message": "Данные успешно обновлены"}), 200

# Выход из аккаунта
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Нет необходимости удалять токен — на стороне клиента он просто теряет актуальность
    return jsonify({"message": "Выход выполнен успешно"}), 200

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)