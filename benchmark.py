import re
import time
import random
import string
from collections import namedtuple

# mock objects
class DedupMailMixin:
    def __init__(self, path):
        self.path = path

class DuplicateSet:
    def __init__(self, pool, conf):
        self.pool = pool
        self.conf = conf

# The original function
def select_matching_path_orig(duplicates):
    assert duplicates.conf["regexp"] is not None
    return {
        mail
        for mail in duplicates.pool
        if re.search(duplicates.conf["regexp"], mail.path)
    }

# The optimized function
def select_matching_path_opt(duplicates):
    assert duplicates.conf["regexp"] is not None
    compiled_regex = re.compile(duplicates.conf["regexp"])
    return {
        mail
        for mail in duplicates.pool
        if compiled_regex.search(mail.path)
    }

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_benchmark():
    # Setup test data
    num_mails = 100000
    pool = set()
    for _ in range(num_mails):
        path = "/var/mail/" + generate_random_string(20)
        # make ~10% match
        if random.random() < 0.1:
            path += "MATCH"
        pool.add(DedupMailMixin(path))

    conf = {"regexp": "MATCH"}
    duplicates = DuplicateSet(pool, conf)

    # Warm up and test original
    print("Testing original...")
    start = time.time()
    for _ in range(10):
        select_matching_path_orig(duplicates)
    orig_time = time.time() - start
    print(f"Original time: {orig_time:.4f}s")

    # Warm up and test optimized
    print("Testing optimized...")
    start = time.time()
    for _ in range(10):
        select_matching_path_opt(duplicates)
    opt_time = time.time() - start
    print(f"Optimized time: {opt_time:.4f}s")

    print(f"Improvement: {orig_time / opt_time:.2f}x faster")

if __name__ == "__main__":
    run_benchmark()
