import hashlib
import random
from typing import List, Optional

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

class MerkleTree:
    def __init__(self, data: List[str]) -> None:
        self.original_data = data
        self.leaves = list(map(sha256, data))
        self.tree: List[List[str]] = [self.leaves]
        self._build_tree()

    def _build_tree(self) -> None:
        current_level = self.tree[0]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = sha256(left + right)
                next_level.append(combined)
            self.tree.insert(0, next_level)
            current_level = next_level

    def get_root(self) -> str:
        return self.tree[0][0]

    def get_proof(self, index: int) -> List[str]:
        proof = []
        num_levels = len(self.tree)
        for level in range(num_levels - 1, 0, -1):
            sibling_index = index ^ 1
            level_nodes = self.tree[level]
            if sibling_index < len(level_nodes):
                proof.append(level_nodes[sibling_index])
            index = index // 2
        return proof

    def verify_proof(self, leaf: str, proof: List[str], root: str, index: int) -> bool:
        current_hash = sha256(leaf)
        for sibling in proof:
            if index % 2 == 0:
                current_hash = sha256(current_hash + sibling)
            else:
                current_hash = sha256(sibling + current_hash)
            index = index // 2
        return current_hash == root

    def get_non_inclusion_proof(self, target: str) -> Optional[dict]:
        target_hash = sha256(target)
        if target_hash in self.leaves:
            return None

        sorted_leaf_pairs = sorted((h, i) for i, h in enumerate(self.leaves))
        for i, (leaf_hash, idx) in enumerate(sorted_leaf_pairs):
            if target_hash < leaf_hash:
                proof_index = sorted_leaf_pairs[i - 1][1] if i > 0 else idx
                return {
                    "target": target,
                    "target_hash": target_hash,
                    "closest_leaf": self.original_data[proof_index],
                    "closest_leaf_index": proof_index,
                    "proof": self.get_proof(proof_index)
                }
        last_index = sorted_leaf_pairs[-1][1]
        return {
            "target": target,
            "target_hash": target_hash,
            "closest_leaf": self.original_data[last_index],
            "closest_leaf_index": last_index,
            "proof": self.get_proof(last_index)
        }

    def verify_non_inclusion(self, proof_data: dict, root: str) -> bool:
        if sha256(proof_data["target"]) == sha256(proof_data["closest_leaf"]):
            return False
        return self.verify_proof(
            proof_data["closest_leaf"],
            proof_data["proof"],
            root,
            proof_data["closest_leaf_index"]
        )

if __name__ == "__main__":
    registros = [str(i) for i in range(1, 101)]
    arvore = MerkleTree(registros)
    raiz = arvore.get_root()
    print(f"Raiz da Árvore de Merkle: {raiz}\n")

    valor_sorteado = str(random.randint(1, 120))
    hash_valor = sha256(valor_sorteado)

    print(f"Valor sorteado: {valor_sorteado}")
    print(f"Hash do valor sorteado: {hash_valor}\n")

    if valor_sorteado in registros:
        index = registros.index(valor_sorteado)
        prova = arvore.get_proof(index)
        valido = arvore.verify_proof(valor_sorteado, prova, raiz, index)
        print(f"O valor '{valor_sorteado}' está incluído na árvore.")
        print("Prova de inclusão válida?", valido)
    else:
        prova_ni = arvore.get_non_inclusion_proof(valor_sorteado)
        if prova_ni:
            valido = arvore.verify_non_inclusion(prova_ni, raiz)
            print(f"O valor '{valor_sorteado}' NÃO está incluído na árvore.")
            print("Prova de não-inclusão válida?", valido)
        else:
            print("Erro: o valor está na árvore, não é possível gerar prova de não-inclusão.")
