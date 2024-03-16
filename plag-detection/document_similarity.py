from dataclasses import dataclass, fields

import threading
import time

# importing own libs
from string_methods import * 

# handles parameters for DocumentSimilarity class
@dataclass
class Parameters:
    token: str
    k_shingles: int
    hf_amount: int
    buckets_amount: int
    bucket_size: int
    
    def calc_threshold(self) -> float:
        b, r = self.buckets_amount, self.bucket_size
        if b <= 0 or r <= 0:
            return -1
        else:
            return (1 / b) ** (1 / r)
    
    def validate_parameters(self) -> bool:
        wrong_fields = []
        
        for field in fields(self):
            value = getattr(self, field.name) 
            
            if isinstance(value, int):
                print(f'field {field.name} -> {value}')
                if value <= 0:
                    wrong_fields.append(field.name)
                if field.name == 'hf_amount':
                    if self.buckets_amount * self.bucket_size != self.hf_amount:
                        wrong_fields.append(field.name)
        return len(wrong_fields) == 0, wrong_fields
        
# class is responsible for finding similar pairs of documents
class DocumentSimilarity:
    def __init__(self, name_list: list, document_list: list, parameters: Parameters) -> None:
        self.name_list = name_list
        self.document_list = document_list
        self.parameters = parameters
        
        # computed during the process
        self.shingled_list = None
        self.sketches_list = None
        self.similar_list = None
        
    # canonizing text with multuthreading
    def canonize_texts(self) -> list:
        # forming groups for threads
        q = 4
        groups_of_four = []
        for i in range(q, len(self.document_list) + 1, q):
            groups_of_four.append(tuple(self.document_list[i-q:i]))
        
         # List to store thread instances
        threads = []

        for row in groups_of_four:
            threads.append(threading.Thread(target=str_manager.canonize, args=(row[0],)))
            threads.append(threading.Thread(target=str_manager.canonize, args=(row[1],)))
            threads.append(threading.Thread(target=str_manager.canonize, args=(row[2],)))
            threads.append(threading.Thread(target=str_manager.canonize, args=(row[3],)))

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        print("\nEverything is fine!")

    # shingling -> minHashing -> and return (also saves as a field) list of sketches (also a list)
    def form_document_sketches_list(self) -> list:
        canonized_list = [str_manager.canonize(doc) for doc in self.document_list]
        
        # forming shingles
        self.shingled_list = [ str_manager.shingling(
                document = doc, 
                token = self.parameters.token,
                k = self.parameters.k_shingles
            ) for doc in canonized_list ]
        
        boolean_matrix = str_manager.boolean_matrix(self.shingled_list)
        signature_matrix = str_manager.min_hash_matrix(boolean_matrix, self.parameters.hf_amount)

        # creating fingerprints for each hash matrix column
        self.sketches_list = str_manager.create_sketches_for_hash_matrix(
                hash_matrix = signature_matrix, 
                num_of_buckets = self.parameters.buckets_amount, 
                bucket_size = self.parameters.bucket_size
            )
        return self.sketches_list
    
    # implements LSH and returns a dict of <(doc_1, doc_2), similatiry>
    def find_consecutive_pairs(self) -> dict:
        lsh = str_manager.lsh(self.sketches_list) 
        self.similar_pairs = str_manager.unwrap_hashmap(lsh, self.parameters.calc_threshold())
        return self.similar_pairs
            
    # forming a similarity list
    def form_similar_docs_list(self) -> list:
        
        n = self.parameters.buckets_amount
        t = self.parameters.calc_threshold()
        
        print('n = ', n)
        similar_list = [(key, value/n) for key, value in self.similar_pairs.items() if value / n > t]
        
        similar_list = []
        for key, value in self.similar_pairs.items():
            if value / n > t:
                jac_sim = str_manager.jaccard_similarity(self.shingled_list[key[0]], self.shingled_list[key[1]])
                if jac_sim > t:
                    similar_list.append((key, jac_sim))

        similar_list.sort(key=lambda x: x[1], reverse=True)
        self.similar_list = similar_list
        return similar_list
            
    # computing similarity for two documents by sketches
    def compute_sketch_similarity(self, index_a: int, index_b: int) -> float:
        n = len(self.sketches_list[index_a])
        both_sim = 0
        for i in range(n):
            if self.sketches_list[index_a][i] == self.sketches_list[index_b][i]:
                both_sim += 1
        
        sketch_similarity = both_sim / n
        return sketch_similarity
    
    # computing similarity by shingles
    def compute_shingle_similarity(self, index_a: int, index_b: int) -> float:
        shingle_similarity = str_manager.jaccard_similarity(
                self.shingled_list[index_a],
                self.shingled_list[index_b]
            )
        return shingle_similarity
    
    def avg_similarity(self) -> float:
        l = [value for key, value in self.similar_list]
        if sum(l) == 0:
            return 0
        return sum(l) / len(l)
    
    def extraxt_text_from_pairs(self) -> str:
        s = ''
        for key, value in self.similar_list:
            s += f"{self.name_list[key[0]]}, {self.name_list[key[1]]} -> {value}\n"
        return s