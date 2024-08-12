from sys import stdout
from time import sleep

jobLen = 100
progressReport = 0

while progressReport < jobLen:
    progressReport += 1
    stdout.write("\r[%s/%s]" % (progressReport, jobLen))
    stdout.flush()
    sleep(0.1)

stdout.write("\n")
stdout.flush()