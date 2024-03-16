import numpy as np
import math

# my own libs
import additional_functions.hash_functions as hf
import setting_files.stop_words as sw

# creating a list of hash functions beforehand
hash_functions_list = hf.CreateHashFunctions.create_functions(num_of_functions=1000)

# manages string canonization, shingling and etc.
class str_manager:
    @staticmethod
    def canonize(document: str, language: str = None) -> str:
        stop_symbols = '.,!?:;-\n\r()'
    
        canonized_str = ''.join([x.lower() for x in document if x not in stop_symbols])
        
        # removing stop-words
        #if language is not None and sw.WORD_SET_DICTIONARY.get(language) is not None:
        #    stop_words = sw.WORD_SET_DICTIONARY.get(language)
        #    canonized_str = ' '.join([word for word in canonized_str.split() if word not in stop_words])
        
        return canonized_str

    # splits a string (document) into k-length shingles
    @staticmethod
    def shingling(document: str, k: int, token: str = None) -> set:
        new_set = set()
        
        source = []
        #source = [letter for letter in document] if token == 'letter' else [word for word in document.split()]
        match token:
            case 'letter':
                source = [letter for letter in document]
            case _:
                source = [word for word in document.split()]

        for i in range(0, len(source) - k + 1):
            inserted_shingle = tuple(source[i:i+k])
            new_set.add(hash(inserted_shingle))
        return new_set
    
    # jaccard similarity implementation
    @staticmethod
    def jaccard_similarity(set_a: set, set_b: set) -> float:
        union = set_a.union(set_b)
        intersection = set_a.intersection(set_b)

        similarity = len(intersection) / len(union)        
        return similarity
    
    # creates a boolean matrix out of all documents and their elements
    @staticmethod
    def boolean_matrix(set_list: list[set]) -> list:
        universal_set = set_list[0].union(*set_list[1:])
        set_list_len = len(set_list)
        
        matrix = [[False]*set_list_len for _ in range(len(universal_set))]
        
        i = 0
        for x in universal_set:
            for j in range(set_list_len):
                if x in set_list[j]:
                    matrix[i][j] = True 
            i += 1
            
        return matrix
    
    # returns a jaccard similarity of two columns
    @staticmethod
    def column_bool_similarity(matrix: list, index_a: int, index_b: int) -> float:
        both_one = 0
        at_least_one = 0
        
        # could I optimize this?
        for row in matrix:
            if row[index_a] and row[index_b]:
                both_one += 1
            if row[index_a] or row[index_b]:
                at_least_one += 1
        
        column_bool_similarity = both_one / at_least_one
        
        return column_bool_similarity
    
    # min_hash_matrix, where k is a number of hash functions
    # i reversed the hash_matrix? so its easier to compute the buckets
    @staticmethod
    def min_hash_matrix(boolean_matrix: list, k: int):
        col_len = len(boolean_matrix[0])
        row_len = len(boolean_matrix)
        
        # getting list of hash functions fron hash_functions.py
        hf_list = hash_functions_list[:k]
        
        # initializing a matrix[col_len][k] of MAX values
        hash_matrix = [[math.inf]*k for _ in range(col_len)]
        
        for r in range(row_len):
            # computing all hash functions
            hash_values = [(hf_list[i](r, k)) for i in range(k)]
            #print("hash values, r = ", r, " size = ", len(set(hash_values)), " | ", len(hash_values))
            
            # iterating through columns
            for c in range(col_len):
                if boolean_matrix[r][c] == True:
                    for i in range(k):
                        hash_matrix[c][i] = min(hash_values[i], hash_matrix[c][i])
                    
        return hash_matrix

    # make a sketch for a cols of hash_matrix
    @staticmethod
    def create_sketches_for_hash_matrix(hash_matrix: list, num_of_buckets: int, bucket_size: int) -> list:
        sketches_list = []
        
        for row in hash_matrix:
            row_buckets = [tuple(row[i:i+bucket_size]) for i in range(0, len(row) - bucket_size + 1, bucket_size)]
            row_sketches = [hash(bucket) for bucket in row_buckets]
            sketches_list.append(row_sketches)
        return sketches_list

    # finding similarity by hash matrix
    @staticmethod
    def jaccard_similarity_hash_matrix(hash_matrix: list, index_a: int, index_b: int) -> float:
        both_same = 0
        for col_a, col_b in zip(hash_matrix[index_a], hash_matrix[index_b]):
            if col_a == col_b:
                both_same += 1
            
        similarity = both_same / len(hash_matrix[index_a])
        
        return similarity

    @staticmethod
    def lsh(sketches_list: list[list]):
        list_of_hash_maps = []
        
        for i in range(len(sketches_list[0])):
            hash_map = {}
            for j in range(len(sketches_list)):
                if hash_map.get(sketches_list[j][i]) is None:
                    hash_map[sketches_list[j][i]] = [j]
                else:
                    hash_map[sketches_list[j][i]].append(j)
            list_of_hash_maps.append(hash_map)
            
        return list_of_hash_maps
    
    @staticmethod
    def unwrap_hashmap(list_of_hash_maps: list[dict], threshold: float):
        similar_pairs = {}
        
        for hash_map in list_of_hash_maps:
            for key, array in hash_map.items():
                # if there are some pairs then we break those list into pairs by two
                for i in range(len(array) - 1):
                    for j in range(i+1, len(array)):
                        pair = tuple([array[i], array[j]])
                        if similar_pairs.get(pair) is None:
                            similar_pairs[pair] = 1
                        else:
                            similar_pairs[pair] += 1

        return similar_pairs
    