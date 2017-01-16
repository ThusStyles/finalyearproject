import psycopg2
from shutil import copyfile
import os
import itertools

SCALE_FACTOR = 0.005
X_GAP = 20


def rwh_primes(n):
    # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
    """ Returns  a list of primes < n """
    sieve = [True] * n
    for i in range(3,int(n**0.5)+1,2):
        if sieve[i]:
            sieve[i*i::2*i] = [False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3,n,2) if sieve[i]]


def overlaps(window_starty, window_endy, starty, endy):
    smaller_than_window = (window_starty <= starty <= window_endy) or (window_starty <= endy <= window_endy)
    bigger_than_window = starty < window_starty and endy > window_endy
    return smaller_than_window or bigger_than_window


def get_prime_array(all_primes, prime_first, prime_last, top_first_val, left_first_val):

    current_column_number = top_first_val
    current_column = [current_column_number]
    new_primes = []

    # Get primes in a better format, list of lists, where each list is a column
    for idx, prime in enumerate(all_primes[prime_first:prime_last]):
        current_column.append(prime)
        if (idx + 1) % 100 == 0:
            new_primes.append(current_column)
            current_column_number += 1
            current_column = [current_column_number]
        elif idx == (len(all_primes[prime_first:prime_last]) - 1):
            new_primes.append(current_column)
            current_column_number += 1
            current_column = [current_column_number]

    # Transpose to make it in the correct format, so we can go line by line in the txt
    new_primes = [list(x) for x in (itertools.zip_longest(*new_primes))]
    transposed_primes = []

    # Write the primes to the file
    current_row_number = " "
    for prime_list in new_primes:
        if current_row_number == " ":
            current_row_number = left_first_val
        else:
            prime_list = [current_row_number] + prime_list
            current_row_number += 1
        prime_list = [x for x in prime_list if x is not None]
        transposed_primes.append(prime_list)

    return transposed_primes


def group_results(results, primes):
    window_starty = results[0][3]
    window_endy = window_starty + results[0][5]

    final_results = []
    current_row = []

    results_length = len(results)

    for idx, result in enumerate(results):
        starty = result[3]
        h = result[5]
        endy = starty + h

        # If we're on the final item, then append and break
        if idx == (results_length - 1):
            # Got to final result
            current_row.append(result)
            final_results.append(current_row)
            break

        # Check if the current component overlaps with the window
        if overlaps(window_starty, window_endy, starty, endy):
            # Update window and add to results
            if starty < window_starty:
                window_starty += ((window_starty - starty) * SCALE_FACTOR)
            if endy > window_endy:
                window_endy += ((endy - window_endy) * SCALE_FACTOR)
            current_row.append(result)
        else:
            # This one doesn't overlap with the window
            final_results.append(current_row)
            window_starty = starty
            window_endy = endy
            current_row = [result]

    # Remove small groups
    final_results = [x for x in final_results if len(x) > 10]

    # Sort by x values in each group
    for idx, result in enumerate(final_results):
        result.sort(key=lambda x: x[2])

    total_final_results = []

    # Put into digit groups by x
    for idx, row in enumerate(final_results):
        current_x = row[0][2] + row[0][4]
        current_row_grouped = []
        current_group = []
        for idx2, result in enumerate(row):
            startx = result[2]
            endx = startx + result[4]
            if startx <= (current_x + X_GAP) or endx == current_x:
                # Is in the current group
                current_x = endx
                current_group.append(result)
            else:
                current_row_grouped.append(current_group)
                current_group = [result]
                current_x = endx
        total_final_results.append(current_row_grouped)

    col = 0

    # Split up big groups into smaller ones
    for idx, row in enumerate(total_final_results[1:]):
        for idx2, digit_group in enumerate(row):
            prev_size = len(row[2]) if idx2 == 0 else len(row[idx2 - 1])
            next_size = len(row[idx2 - 1]) if idx2 == (len(row) - 1) else len(row[idx2 + 1])
            if len(digit_group) > (prev_size + next_size):
                # Need to split into smaller
                new_digit_groups = []
                local_digits = []
                for idx3, digit in enumerate(digit_group):
                    if digit[4] > 8 and digit[5] > 8:
                        # Then we can append
                        local_digits.append(digit)
                        if idx3 == (len(digit_group) - 1):
                            new_digit_groups.append(local_digits)
                    else:
                        # Its a small dot, so empty
                        new_digit_groups.append(local_digits)
                        local_digits = []
                # Append the new groups
                del row[idx2]
                row[idx2:idx2] = new_digit_groups
        col += 1

    labeled_results = []

    for idx, row in enumerate(total_final_results):
        for idx2, digit_group in enumerate(row):
            matching_value = primes[idx][idx2]
            group_length = len(digit_group)
            value_length = len(str(matching_value))
            if group_length != value_length: continue
            # Each digit label value
            for idx3, digit in enumerate(digit_group):
                new_digit = digit + (int(str(matching_value)[idx3]),)
                labeled_results.append(new_digit)

    return labeled_results


def main():
    all_primes = rwh_primes(100000)
    primes_870 = get_prime_array(all_primes, 0, 2500, 0, 1)
    primes_871 = get_prime_array(all_primes, 2500, 5000, 25, 1)
    primes_872 = get_prime_array(all_primes, 5000, 7500, 50, 1)
    primes_873 = get_prime_array(all_primes, 7500, 10000, 75, 1)


    # Connect to DB
    conn = psycopg2.connect("dbname=fyp user=theostyles")
    cur = conn.cursor()

    cur.execute("SELECT id, cc_image, x, y, w, h FROM moments WHERE page = 884 AND y BETWEEN 500 AND 5500 ORDER BY y ASC;")
    results_870 = cur.fetchall()

    cur.execute("SELECT id, cc_image, x, y, w, h FROM moments WHERE page = 885 AND y BETWEEN 500 AND 5500 ORDER BY y ASC;")
    results_871 = cur.fetchall()

    cur.execute("SELECT id, cc_image, x, y, w, h FROM moments WHERE page = 886 AND y BETWEEN 500 AND 5450 ORDER BY y ASC;")
    results_872 = cur.fetchall()

    cur.execute("SELECT id, cc_image, x, y, w, h FROM moments WHERE page = 887 AND y BETWEEN 490 AND 5500 ORDER BY y ASC;")
    results_873 = cur.fetchall()

    labeled_870 = group_results(results_870, primes_870)
    labeled_871 = group_results(results_871, primes_871)
    labeled_872 = group_results(results_872, primes_872)
    labeled_873 = group_results(results_873, primes_873)
    current_page = 884
    all_labeled = [labeled_870, labeled_871, labeled_872, labeled_873]
    totals = [len(x) for x in all_labeled]
    print("TOTAL SAMPLES", "\n870:", totals[0], "\n871:", totals[1], "\n872:", totals[2], "\n873:", totals[3], "\nALL:", sum(totals))

    base_dir = "/Users/theostyles/PycharmProjects/extractLetters/"
    # Empty results
    for x in range(10):
        dir = base_dir + str(x)
        os.chdir(dir)
        filelist = [f for f in os.listdir(dir) if f.endswith(".tif")]
        for f in filelist: os.remove(f)

    # Copy the right file across
    for labeled_set in all_labeled:
        for result in labeled_set:
            digit = result[-1]
            file_name = result[1]
            copyfile(base_dir + "page-0" + str(current_page) + "/" + file_name, base_dir + str(digit) + "/" + file_name)
        current_page += 1

    cur.close()
    conn.close()

main()
