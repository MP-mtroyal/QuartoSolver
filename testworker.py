def workerListConstructor(values, startIndex, numWorkers, numPerWorker):
    results = []
    index = startIndex
    for i in range(numWorkers):
        workerValues = []
        for n in range(numPerWorker):
            if index >= len(values):
                if len(workerValues) > 0:
                    results.append(workerValues)
                return results, index - startIndex
            workerValues.append(values[index])
            index += 1
        results.append(workerValues)
    return results, index - startIndex

arr = [i for i in range(20)]
print(workerListConstructor(arr, 12, 3, 4))