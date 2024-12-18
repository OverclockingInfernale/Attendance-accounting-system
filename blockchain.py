import json, hashlib, time
from models import Block as BlockModel, Transaction as TransactionModel
from db import db

class Block:
    def __init__(self, transactions, previous_hash, difficulty=2, nonce=0, timestamp=None):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = nonce  # взял из гугла - Nonces are used in proof-of-work systems to vary the input to a cryptographic hash function
                            # so as to obtain a hash for a certain input that fulfils certain arbitrary conditions.
                            # в нашем случае, для того чтоб подобрать нужный хэш
        self.timestamp = timestamp if timestamp else time.time()
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_str = json.dumps({
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()

class Blockchain:
    difficulty = 2              # колическо нулей в начале, чем больше, тем сложнее сгенеририровать код (аля это у нас нагрузка создается для майнеров)
    def __init__(self):
                                 # тут загржается наша цепочка из бд
        self.chain = self.load_chain_from_db()
        if not self.chain:
                            # генезис блок - первоначальный блок, начало цепочки
            genesis = Block([], "0", difficulty=self.difficulty)
            genesis.hash = genesis.compute_hash()
            self.save_block_to_db(genesis, [])
            self.chain = [genesis]

    def load_chain_from_db(self): # всякие манипуляции чтоб получить цепочку из бд, так сказать восстановиться
        blocks = BlockModel.query.order_by(BlockModel.id).all()
        chain = []
        for b in blocks:
            txs = [t.data for t in b.transactions]
            block = Block(txs, b.previous_hash, difficulty=b.difficulty, nonce=b.nonce, timestamp=b.timestamp)
            block.hash = b.hash
            chain.append(block)
        return chain

    def save_block_to_db(self, block, transactions): # тут понятно, после создания в блокчейне заносим его в базу чтоб не потерять в нашей псевдо модели
        bmodel = BlockModel(
            hash=block.hash,
            previous_hash=block.previous_hash,
            nonce=block.nonce,
            timestamp=block.timestamp,
            difficulty=block.difficulty
        )
        db.session.add(bmodel)
        db.session.flush()

        for tx_data in transactions:
            tmodel = TransactionModel(block_id=bmodel.id, data=tx_data)
            db.session.add(tmodel)

        db.session.commit()

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        if block.previous_hash != self.get_last_block().hash:
            return False
        if not block.hash.startswith("0" * self.difficulty):
            return False
        self.chain.append(block)
        self.save_block_to_db(block, block.transactions)
        return True

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i-1]
            if cur.hash != cur.compute_hash():
                return False
            if cur.previous_hash != prev.hash:
                return False
        return True
