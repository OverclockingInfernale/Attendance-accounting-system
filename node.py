from blockchain import Blockchain, Block

class Node:
    def __init__(self):
        self.blockchain = Blockchain()
        self.unconfirmed_transactions = []

        # создаем транзакцию, тут по сути то что мы делаем на вебке, и в целом, это все транзакции, их мы пуляем в этот пул,
        # который потом нам надо подвтердить типа майнерами (как раз тут схема идет пруф оф ворк) и созадается блок, сам блок и отвечает за то что транзакция в сети, типа
    def create_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

        # ну тут и осздаем блок, точнее майним, тут сведено это до части что мы просто берем последний блок в цепочке,
        # и к нему пристыковываем новый с нашими транзакциями, все очен просто, ненадежно, но простите нас и поймите
    def mine_block(self):
        if not self.unconfirmed_transactions:
            return None
        last_block = self.blockchain.get_last_block()
        new_block = Block(self.unconfirmed_transactions, last_block.hash, difficulty=self.blockchain.difficulty)

        while not new_block.hash.startswith("0" * self.blockchain.difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        if self.blockchain.add_block(new_block):
            self.unconfirmed_transactions = []
            return new_block
        return None
