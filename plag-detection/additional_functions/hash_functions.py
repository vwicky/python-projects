import random
import sympy

# manages hash functions (for np_array)
class HashFunctionsManager:
    def __init__(self, amount_of_primes: int, mod: int) -> None:
        self.n = amount_of_primes
        self.mod = mod
        self.prime_list = self.get_prime_list(self.n)
    
    def hash_func(self, rlist: list) -> int:
        sumh = 0
        for i in range(len(rlist)):
            sumh += self.prime_list[i % self.mod] * rlist[i]
        return int(sumh) % self.mod
    
    @staticmethod    
    def get_prime_list(n = 100) -> list:
        min_prime, max_prime = 11, 1000
        return [sympy.randprime(min_prime, max_prime) for _ in range(n)]
    
# has a static method that creates a list of random hash functions
class CreateHashFunctions:        
    @staticmethod
    def create_functions(num_of_functions: int) -> list:
        all_funcs = []
        pr = HashFunctionsManager.get_prime_list()
        
        for _ in range(num_of_functions):
            coef = [random.choice(pr), random.choice(pr), random.choice(pr)]
            coef = [random.randint(1, 100), random.randint(1, 100), random.choice(pr)]
            all_funcs.append(lambda x, mod, c=coef: ((c[0]*x + c[1]) % c[2] % mod))
        return all_funcs
