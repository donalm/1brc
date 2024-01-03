# time python3 calculateAverage.py
import os
import multiprocessing as mp


def get_file_chunks(
    file_name: str,
    max_cpu: int = 8,
) -> list:
    """Split flie into chunks"""
    cpu_count = min(max_cpu, mp.cpu_count())

    file_size = os.path.getsize(file_name)
    chunk_size = file_size // cpu_count

    start_end = list()
    with open(file_name, "r") as f:

        def is_new_line(position):
            if position == 0:
                return True
            else:
                f.seek(position - 1)
                return f.read(1) == "\n"

        def next_line(position):
            f.seek(position)
            f.readline()
            return f.tell()

        chunk_start = 0
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + chunk_size)

            while not is_new_line(chunk_end):
                chunk_end -= 1

            if chunk_start == chunk_end:
                chunk_end = next_line(chunk_end)

            start_end.append(
                (
                    file_name,
                    chunk_start,
                    chunk_end,
                )
            )

            chunk_start = chunk_end

    return (
        cpu_count,
        start_end,
    )


def _process_file_chunk(
    file_name: str,
    chunk_start: int,
    chunk_end: int,
) -> dict:
    """Process each file chunk in a different process"""
    result = dict()
    with open(file_name, "r") as f:
        f.seek(chunk_start)
        for line in f:
            chunk_start += len(line)
            if chunk_start > chunk_end:
                break
            location, measurement = line.split(";")
            measurement = float(measurement)
            if location not in result:
                result[location] = [
                    measurement,
                    measurement,
                    measurement,
                    1,
                ]  # min, max, sum, count
            else:
                if measurement < result[location][0]:
                    result[location][0] = measurement
                if measurement > result[location][1]:
                    result[location][1] = measurement
                result[location][2] += measurement
                result[location][3] += 1
    return result


def process_file(
    cpu_count: int,
    start_end: list,
) -> dict:
    """Process data file"""
    with mp.Pool(cpu_count) as p:
        # Run chunks in parallel
        chunk_results = p.starmap(
            _process_file_chunk,
            start_end,
        )

    # Combine all results from all chunks
    result = dict()
    for chunk_result in chunk_results:
        for location, measurements in chunk_result.items():
            if location not in result:
                result[location] = measurements
            else:
                if measurements[0] < result[location][0]:
                    result[location][0] = measurements[0]
                if measurements[1] > result[location][1]:
                    result[location][1] = measurements[1]
                result[location][2] += measurements[2]
                result[location][3] += measurements[3]

    # Print final results
    results_calculated = dict()
    for location, measurements in sorted(result.items()):
        results_calculated[
            location
        ] = f"{measurements[0]:.1f}/{(measurements[2] / measurements[3]) if measurements[3] !=0 else 0:.1f}/{measurements[1]:.1f}"
    return results_calculated


if __name__ == "__main__":
    cpu_count, *start_end = get_file_chunks("measurements.txt")
    print(process_file(cpu_count, start_end[0]))
