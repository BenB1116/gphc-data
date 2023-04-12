import pandas as pd
import os
import multiprocessing as mp
import time

inv_df = pd.read_csv(r"C:\Users\Ben\Desktop\gphc-data\inv_data_gr.csv")

inv_list = inv_df['gr_id'].values.tolist()

csv_book_mapping = {}

with open(r"C:\Users\Ben\Desktop\gphc-data\book_id_map.csv", "r") as f:
    while True:
        line = f.readline()
        if not line:
            break
        csv_id, book_id = line.strip().split(",")
        csv_book_mapping[csv_id] = book_id

def process_line(line):
    user_id, csv_id, _, rating, _ = line.split(",")

    try:
        rating = int(rating)
    except ValueError:
        rating = 0
    
    try:
        book_id = int(csv_book_mapping[csv_id])
        if rating >= 4 and book_id in inv_list:
            return (user_id, book_id)
        else:
            return (-1, -1)
    except KeyError:
        return (-1, -1)
    
    
def process_chunk(file_name, chunk_start, chunk_end):
    chunk_results = []
    with open(file_name, 'r') as f:
        # Moving stream position to `chunk_start`
        f.seek(chunk_start)

        # Read and process lines until `chunk_end`
        for line in f:
            chunk_start += len(line)
            if chunk_start > chunk_end:
                break
            chunk_results.append(process_line(line))
    return chunk_results

def parallel_read(file_name):
    # Maximum number of processes we can run at a time
    cpu_count = mp.cpu_count()
    print(f'CPU Count: {cpu_count}')

    file_size = os.path.getsize(file_name)
    print(f'File Size: {file_size}')
    chunk_size = file_size // cpu_count
    print(f'Chunk Size: {chunk_size}')


    #1048576
    # Arguments for each chunk (eg. [('input.txt', 0, 32), ('input.txt', 32, 64)])
    chunk_args = []
    with open(file_name, 'r') as f:
        def is_start_of_line(position):
            if position == 0:
                return True
            # Check whether the previous character is EOL
            f.seek(position - 1)
            return f.read(1) == '\n'

        def get_next_line_position(position):
            # Read the current line till the end
            f.seek(position)
            f.readline()
            # Return a position after reading the line
            return f.tell()

        chunk_start = 0
        # Iterate over all chunks and construct arguments for `process_chunk`
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + chunk_size)

            # Make sure the chunk ends at the beginning of the next line
            while not is_start_of_line(chunk_end):
                chunk_end -= 1

            # Handle the case when a line is too long to fit the chunk size
            if chunk_start == chunk_end:
                chunk_end = get_next_line_position(chunk_end)

            # Save `process_chunk` arguments
            args = (file_name, chunk_start, chunk_end)
            chunk_args.append(args)

            # Move to the next chunk
            chunk_start = chunk_end

    with mp.Pool(cpu_count) as p:
        # Run chunks in parallel
        chunk_results = p.starmap(process_chunk, chunk_args)

    results = []
    # Combine chunk results into `results`
    for chunk_result in chunk_results:
        for result in chunk_result:
            results.append(result)

    return results

if __name__ == '__main__':
    time_start = time.time()
    result = parallel_read(r"C:\Users\Ben\Desktop\gphc-data\goodreads_interactions.csv")
    time_end = time.time()
    print(f'Done: {time_end - time_start}')

    with open('interactions.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(f'{int(pair[0])}, {pair[1]}' for pair in result if pair[0] != -1))

