from time import perf_counter

#sorting algorithms
def quicksort_records(records, key_name, reverse=False):
    if len(records) <= 1:
        return records

    pivot_value = records[len(records) // 2].get(key_name)
    lower = []
    equal = []
    higher = []

    for record in records:
        record_value = record.get(key_name)
        if record_value < pivot_value:
            lower.append(record)
        elif record_value > pivot_value:
            higher.append(record)
        else:
            equal.append(record)

    sorted_records = quicksort_records(lower, key_name) + equal + quicksort_records(higher, key_name)
    return list(reversed(sorted_records)) if reverse else sorted_records


def merge_records(left, right, key_name):
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index].get(key_name) <= right[right_index].get(key_name):
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def mergesort_records(records, key_name, reverse=False):
    if len(records) <= 1:
        return records

    midpoint = len(records) // 2
    left_half = mergesort_records(records[:midpoint], key_name)
    right_half = mergesort_records(records[midpoint:], key_name)
    sorted_records = merge_records(left_half, right_half, key_name)
    return list(reversed(sorted_records)) if reverse else sorted_records


def heapify(records, heap_size, root_index, key_name):
    largest_index = root_index
    left_child = (2 * root_index) + 1
    right_child = (2 * root_index) + 2

    if left_child < heap_size and records[left_child].get(key_name) > records[largest_index].get(key_name):
        largest_index = left_child

    if right_child < heap_size and records[right_child].get(key_name) > records[largest_index].get(key_name):
        largest_index = right_child

    if largest_index != root_index:
        records[root_index], records[largest_index] = records[largest_index], records[root_index]
        heapify(records, heap_size, largest_index, key_name)


def heapsort_records(records, key_name, reverse=False):
    sorted_records = records.copy()
    record_count = len(sorted_records)

    for index in range((record_count // 2) - 1, -1, -1):
        heapify(sorted_records, record_count, index, key_name)

    for index in range(record_count - 1, 0, -1):
        sorted_records[0], sorted_records[index] = sorted_records[index], sorted_records[0]
        heapify(sorted_records, index, 0, key_name)

    return list(reversed(sorted_records)) if reverse else sorted_records


def selectionsort_records(records, key_name, reverse=False):
    sorted_records = records.copy()
    record_count = len(sorted_records)

    for left_index in range(record_count):
        min_index = left_index
        for right_index in range(left_index + 1, record_count):
            if sorted_records[right_index].get(key_name) < sorted_records[min_index].get(key_name):
                min_index = right_index
        sorted_records[left_index], sorted_records[min_index] = sorted_records[min_index], sorted_records[left_index]

    return list(reversed(sorted_records)) if reverse else sorted_records


def insertionsort_records(records, key_name, reverse=False):
    sorted_records = records.copy()

    for index in range(1, len(sorted_records)):
        current_record = sorted_records[index]
        current_value = current_record.get(key_name)
        compare_index = index - 1

        while compare_index >= 0 and sorted_records[compare_index].get(key_name) > current_value:
            sorted_records[compare_index + 1] = sorted_records[compare_index]
            compare_index -= 1

        sorted_records[compare_index + 1] = current_record

    return list(reversed(sorted_records)) if reverse else sorted_records


def bubblesort_records(records, key_name, reverse=False):
    sorted_records = records.copy()
    record_count = len(sorted_records)

    for pass_index in range(record_count):
        swapped = False
        for compare_index in range(0, record_count - pass_index - 1):
            if sorted_records[compare_index].get(key_name) > sorted_records[compare_index + 1].get(key_name):
                sorted_records[compare_index], sorted_records[compare_index + 1] = (
                    sorted_records[compare_index + 1],
                    sorted_records[compare_index],
                )
                swapped = True
        if not swapped:
            break

    return list(reversed(sorted_records)) if reverse else sorted_records


def time_record_sort(sort_function, records, key_name, reverse=False):
    start_time = perf_counter()
    sorted_records = sort_function(records.copy(), key_name, reverse)
    elapsed_time = perf_counter() - start_time
    return sorted_records, elapsed_time


SORT_FUNCTIONS = {
    "quick": ("Quick Sort", quicksort_records, "Best/Average: O(n log n), Worst: O(n^2)"),
    "merge": ("Merge Sort", mergesort_records, "Best/Average/Worst: O(n log n)"),
    "heap": ("Heap Sort", heapsort_records, "Best/Average/Worst: O(n log n)"),
    "selection": ("Selection Sort", selectionsort_records, "Best/Average/Worst: O(n^2)"),
    "insertion": ("Insertion Sort", insertionsort_records, "Best: O(n), Average/Worst: O(n^2)"),
    "bubble": ("Bubble Sort", bubblesort_records, "Best: O(n), Average/Worst: O(n^2)"),
}
