import hashlib
import json
from time import time


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index  # Индекс блока
        self.timestamp = timestamp  # Время создания блока
        self.data = data  # Данные о посещаемости
        self.previous_hash = previous_hash  # Хеш предыдущего блока
        self.hash = self.hash_block()  # Хеш текущего блока

    def hash_block(self):
        block_content = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_content).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Создаем генезис-блок
        genesis_block = Block(0, time(), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def add_block(self, data):
        # Добавляем новый блок в цепочку
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), time(), data, previous_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        # Проверяем целостность цепочки
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.previous_hash != previous.hash:
                return False

            if current.hash != current.hash_block():
                return False

        return True

