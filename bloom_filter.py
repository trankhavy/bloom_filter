from bitarray import bitarray
import hashlib
import mmh3
import math
import numpy as np

def hash_function(item, num_hash, num_bits):

        """ Hash function used: Murmur3. Setting different seed every time for num_hash times """

        hashes = []
        for i in range(num_hash):
            temp = mmh3.hash(item, i) % num_bits
            hashes.append(temp)
        return hashes

class Bloom_Filter(object):

    def __init__(self,capacity=100,error_rate=0.05):

        """
        Input:
        n: The number of elements that this Bloom Filter must be able to handle
        error_rate: The false positive error rate
        """

        # Check if the input making sense:

        if capacity < 0:
            raise ValueError("Capacity of the Bloom filter must be a positive number")
        if not (0 < error_rate < 1):
            raise ValueError("Error rate must be between 0 and 1")

        # Setting up
        self.capacity = capacity
        self.error_rate = error_rate
        self.count = 0

        # Calculate m and k in which m is the number of bits we need for the bitarray and k is the number of hash functions needed
        # Formula for m = - n*ln(p) / ((ln(2))^2)
        self.num_bits = int((-self.capacity*math.log(self.error_rate)) / ((math.log(2))**2))
        # Formula for k = (m/n)*ln(2)
        self.num_hash = int((self.num_bits/self.capacity)*math.log(2))


        # Bit array of given size
        self.bit_array = bitarray(int(self.num_bits))

        # initialize all bits as 0
        self.bit_array.setall(False)

    def add(self, item):

        """ Add a new item into the filter """

        # Check if the array has reached its capacity
        if self.count >= self.capacity:
            raise ValueError("Bloom filter has achieved its max capacity")
        else:
            key = hash_function(item, self.num_hash, self.num_bits)
            for k in key:
                self.bit_array[k] = True
            self.count += 1


    def check(self, item):

        """ Check if an item is in the filter. Return True if it is. Otherwise, return False"""

        key = hash_function(item, self.num_hash, self.num_bits)
        for k in key:
            if self.bit_array[k] == False:
                return False
        return True

"""
### Test Bloom Filter ###

bf = Bloom_Filter(21,0.05)
print("Capacity: {}".format(bf.capacity))
print("False positive rate: {}".format(bf.error_rate))
print("Number of bits in bit array is: {}".format(bf.num_bits))
print("Number of hash function: {}".format(bf.num_hash))


from random import shuffle
from random import seed

word_present = ['abound','abounds','abundance','abundant','accessable',
                'bloom','blossom','bolster','bonny','bonus','bonuses',
                'coherent','cohesive','colorful','comely','comfort',
                'gems','generosity','generous','generously','genial']

# word not added
word_absent = ['bluff','cheater','hate','war','humanity',
               'racism','hurt','nuke','gloomy','facebook',
               'geeksforgeeks','twitter']

for item in word_present:
    bf.add(item)
seed(1)
shuffle(word_present)
shuffle(word_absent)

test_words = word_present[:10] + word_absent
shuffle(test_words)
for word in test_words:
    if bf.check(word):
        if word in word_absent:
            print("'{}' is a false positive!".format(word))
        else:
            print("'{}' is probably present!".format(word))
    else:
        print("'{}' is definitely not present!".format(word))

"""
### Question 5 ###
import requests
from random import seed
from random import shuffle

word_site = "https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
response = requests.get(word_site)
words = response.content.splitlines()
seed(1)
shuffle(words)
words_present = words[:len(words)//2]
words_absent = words[len(words)//2:]
shuffle(words_present)
shuffle(words_absent)

true_positive = []
false_positive = []
true_negative = []
false_negative = []

epoch = 13
for i in range(1,epoch):
    batch_size = i*1000
    bloom_filter = Bloom_Filter(batch_size, 0.05) # Define error rate at 5%
    batch_words_present = words_present[:batch_size]
    batch_words_absent = words_absent[:batch_size]
    batch_test = batch_words_present + batch_words_absent
    true_positive_rate = 0
    false_positive_rate = 0
    true_negative_rate = 0
    false_negative_rate = 0

    for word in batch_words_present:
        bloom_filter.add(word)
    for word in batch_test:
        if bloom_filter.check(word) == True and (word in batch_words_present):
            true_positive_rate += 1
        elif bloom_filter.check(word) == True and (word in batch_words_absent):
            false_positive_rate += 1
        elif bloom_filter.check(word) == False and (word in batch_words_absent):
            true_negative_rate += 1
        elif bloom_filter.check(word) == False and (word in batch_words_present):
            false_negative_rate += 1

    true_positive.append(true_positive_rate)
    false_positive.append(false_positive_rate)
    true_negative.append(true_negative_rate)
    false_negative.append(false_negative_rate)

print(true_positive)
print(false_positive)
print(true_negative)
print(false_negative)

### Scalable Bloom Filter ###
class Scalable_Bloom_Filter(object):
    low_growth = 2      # Lower growth rate, take up memory slower
    high_growth = 4     # Faster growth rate, take up memory faster

    def __init__(self, initial_capacity=100, error_rate=0.05, mode=low_growth, ratio=0.9):
        # Check for correct input
        if initial_capacity <= 0:
            raise ValueError("Initial capacity must be a positive number")
        if error_rate < 0 or error_rate > 1:
            raise ValueError("Error rate must be a number between 0 and 1")

        self.initial_capacity = initial_capacity
        self.error_rate = error_rate
        self.ratio = ratio
