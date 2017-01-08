# We will use "hypothesis" for property-based testing à la quickcheck:
# http://hypothesis.readthedocs.io/en/master/quickstart.html
from hypothesis import given
from hypothesis.strategies import text,lists,integers

############################################################################
############################### Quicksort - I ##############################

# partition(xs) picks a pivot in xs and returns a triple of elements of xs
# smaller than the pivot, the pivot, and elements (strictly) larger than the
# pivot.
def partition(xs):
    pivot = xs[0]
    le, gt = [], []
    for x in xs[1:]:
        if x <= pivot:
            le.append(x)
        else:
            gt.append(x)
    return (le, pivot, gt)

# quicksort works by picking *a pivot* and partitioning the input into a batch
# of *smaller elements* and a batch of *larger elements*. Once these three data
# are available, the sub-partitions can be sorted recursively, then combined to
# yield the sorted list.
def quicksort(xs):
    if xs == []:
        return xs
    else:
        le, pivot, gt = partition(xs)
        return (quicksort(le) + [pivot] + quicksort(gt))


############################### Testing #################################

# We define a type generic test function for quicksort by comparing it to
# Python's built-in sort method. If everything is fine, it will be silent,
# otherwise it points out what input provoked the error.
def test_quicksort(lst):
    q = quicksort(lst)
    lst.sort()
    assert (q == lst)

# Here we define two instances of this test, one with lists of strings and one
# with lists of integers. Try these!
@given(lists(text()))
def test_quicksort_text(lst):
    test_quicksort(lst)

@given(lists(integers()))
def test_quicksort_int(lst):
    test_quicksort(lst)


###########################################################################
############################### Quicksort - II ############################

# Our first implementation of partition has to allocate two auxiliary lists
# that the original list gets partitioned into, resulting in a space use
# linearly dependent on the size of the input. We say that partition has
# "linear space complexity", or that it "uses O(n) space".

# Partition can be implemented to run using constant memory space by moving
# around the elements of the input list *without allocating auxiliary list*
# instead.
#
# hackers like this kind of thing; they also save space by using shrt fnctn
# names.

def prtn(xs, lo, hi):

    # pick a pivot
    pvt = xs[hi]
    # keep track of the position of the last element less or equal to the pivot
    le = lo - 1

    # walk through the list
    for i in range(lo, hi):
        # if an element is smaller than the pivot
        if xs[i] <= pvt:
            # increment the ≤ counter and exchange the current element with the
            # element at the new counter position
            le += 1
            xs[le], xs[i] = xs[i], xs[le] # swap

    # of course also the pivot is less-or-equal to itself, so we swap it in its
    # place
    le += 1
    xs[le], xs[hi] = xs[hi], xs[le]

    # report the position of the pivot
    return le


# Sort the list xs between the bounds lo and hi
def qsrt_bounded(xs, lo, hi):
    if lo >= hi:
        return
    pvt = prtn(xs, lo, hi)
    qsrt_bounded(xs, lo, pvt-1)
    qsrt_bounded(xs, pvt+1, hi)

# Finally, sort a list by sorting it from beginning to end.
def qsrt(xs):
    qsrt_bounded(xs, 0, len(xs) - 1)



############################### Testing #################################

# tests like for "quicksort"
def test_qsrt(lst):
    q = lst.copy()
    lst.sort()
    qsrt(q)
    assert (q == lst)

@given(lists(text()))
def test_qsrt_text(lst):
    test_qsrt(lst)

@given(lists(integers()))
def test_qsrt_int(lst):
    test_qsrt(lst)



# a function to run all the tests
def run_tests():
    test_quicksort_text()
    test_quicksort_int()
    test_qsrt_text()
    test_qsrt_int()




###############################################################################
############################### Benchmarking ##################################
###############################################################################


# We will compare the execution time of quicksort, qsrt and Python's .sort() by
# running them on random lists and arrays of different sizes.

# To benchmark your implementations, the interesting functions are
# time_qsrt_list, time_quicksort_list, time_builtin_sort_list and run_timers.


import random
import array
import timeit


# Generate n random lists
def gen_lists(n, len, max=2**10):
    return [ [ random.randint(0,max) for i in range(len) ] for j in range(n) ]

# Same for arrays
def gen_arrays(n, len, max=2**10):
    return [ array.array('i', l) for l in gen_lists(n, len, max) ]

# How long does it take the function "sort" to process n_lists of length len,
# as generated by "generator" ?
def timer(sort, n_lists, len, generator):
    return timeit.timeit('[ {}(l) for l in lists ]'.format(sort),
                         setup = 'lists = {}({}, {})'.format(generator, n_lists, str(2**len)),
                         globals=globals(),
                         # the sorting is effectful code, run only once per generated data!
                         number = 1)

# Use "generator" to generate n_lists random lists/arrays of lengths between 2**minlen
# and 2**maxlen and sort them using the function "sort"
def time_srt(sort, generator, n_lists = 1000, minlen = 0, maxlen = 9):
    res = "Algorithm: {}, Random generator: {}\n".format(sort, generator)
    for len in range(minlen, maxlen + 1):
        t = timer(sort, n_lists, len, generator)
        res = "{}length: {:4}\ttime: {:.7} s\n".format(res, 2**len, t)
    print(res)


# The built-in sorting algorithm wrapped as a function for use in time_srt.
# May or may not sort the input, run for side-effects only.
def builtin_sort(xs):
    list(xs).sort()


def time_qsrt_list():
    time_srt("qsrt", "gen_lists")
def time_quicksort_list():
    time_srt("quicksort", "gen_lists")
def time_builtin_sort_list():
    time_srt("builtin_sort", "gen_lists")

def time_qsrt_array():
    time_srt("qsrt", "gen_arrays")
def time_quicksort_array():
    time_srt("quicksort", "gen_arrays")
def time_builtin_sort_array():
    time_srt("builtin_sort", "gen_arrays")

def run_timers():
    time_qsrt_list()
    time_quicksort_list()
    time_builtin_sort_list()
    # time_qsrt_array()
    # time_quicksort_array()
    # time_builtin_sort_array()

# If called as a program, run the tests, then the timers.
if __name__ == '__main__':
    run_tests()
    run_timers()
