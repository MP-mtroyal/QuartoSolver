import time

class Profiler:
    def __init__(self):
        self.profiles = {}
        self.paused = True
        self.timer = time.perf_counter_ns()
        self.lastTitle = None
        self.startTime = time.perf_counter_ns()
        self.longestTitle = 20


    def reset(self):
        self.timer = time.perf_counter_ns()

    def fullReset(self):
        self.reset()
        self.profiles = {}
        self.startTime = time.perf_counter_ns()


    def pause(self):
        self.paused = True
        self._logLast()


    def unpause(self):
        self.paused = False
        self.timer = time.perf_counter_ns()

    def _logLast(self):
        delta = time.perf_counter_ns() - self.timer
        self.timer = time.perf_counter_ns()
        if self.lastTitle != None:
            if self.lastTitle not in self.profiles:
                self.profiles[self.lastTitle] = (delta, 1)
                self.longestTitle = max(self.longestTitle, len(self.lastTitle))
            else:
                accumTime, count = self.profiles[self.lastTitle]
                self.profiles[self.lastTitle] = (accumTime+delta, count+1)
        self.lastTitle = None

    def log(self, title):
        self._logLast()
        self.lastTitle = title

    def print(self):
        totalTime = time.perf_counter_ns() - self.startTime
        titleHeader = "  --  Title "
        while len(titleHeader) < self.longestTitle: titleHeader += " "
        print(f'{titleHeader}\t|\tTotal Time\t|\tCount')
        print("-------------------------------------------------------")
        acountedTime = 0
        for title in self.profiles.keys():
            paddedTitle = title
            while len(paddedTitle) < self.longestTitle:
                paddedTitle += " "
            accumTime, count = self.profiles[title]
            acountedTime += accumTime
            print(f' - {paddedTitle}\t|\t{accumTime / 1_000_000_000 :.06f}\t|\t{count}')

        print(f'Total Time: {totalTime / 1_000_000_000 :.05f} | Missing Time: {(totalTime - acountedTime) / 1_000_000_000 :.05f}')
