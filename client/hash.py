
import random, string
import hashlib

def get_random_string(length):

    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

def get_sha512(sentence):

    hash_object = hashlib.sha512(sentence.encode())
    return hash_object.hexdigest()