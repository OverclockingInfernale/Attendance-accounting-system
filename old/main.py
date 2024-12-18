from flask import Flask, request, jsonify, render_template
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

# Главная страница
@app.route('/')
def home():
    return render_template('index.html')

# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Логика регистрации пользователя
    return jsonify({"message": "User registered successfully"}), 201

# Запись посещаемости
@app.route('/attendance', methods=['POST'])
def attendance():
    data = request.get_json()
    blockchain.add_block(data)
    return jsonify({"message": "Attendance recorded"}), 201

# Просмотр цепочки блоков
@app.route('/chain', methods=['GET'])
def chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        })
    return jsonify({"length": len(chain_data), "chain": chain_data})

if __name__ == '__main__':
    app.run(debug=True)
