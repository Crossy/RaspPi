import os
import xively
import subprocess
import time
import datetime
import requests
import random

FEED_ID = "468241028"
API_KEY = "K75wWfFgpuGvvxJLHFCcCzaV3UBm4bR6MmzhyIaJJgRjKAkg"
DEBUG = True

class xivelyHelper:     #Change name probably
    def __init__(self,feed_id,api_key,debug=False):
        self.feed_id = feed_id
        self.debug = debug
        # initialize api client
        self.api = xively.XivelyAPIClient(api_key)
        self.feed = self.api.feeds.get(feed_id)
        self.datastream = None

    # function to return a datastream object.
    def get_datastream(self, datastream):
      try:
        datastream = self.feed.datastreams.get(datastream)
        if self.debug:
          print "Found existing datastream"
        self.datastream = datastream
        return True
      except:
        print "Datastream doesn't exist, use create_datastream to create new datastream"
        return False

    def create_datastream(self, datastream, tags="", min_value=None, max_value=None):
        datastream = self.feed.datastreams.create(datastream, tags)
        datastream.max_value = max_value
        datastream.min_value = min_value
        self.datastream = datastream
        if self.debug:
          print "Created new datastream " + datastream
        return True

    def put_datapoint(self,datapoint):
        self.datastream.current_value = datapoint
        self.datastream.at = datetime.datetime.utcnow()
        try:
          self.datastream.update()
        except requests.HTTPError as e:
          print "HTTPError({0}): {1}".format(e.errno, e.strerror)
        if self.debug:
            print "Updating Xively feed with value: %s" % datapoint

# main program entry point - runs continuously updating our datastream with the
# current 1 minute load average
def main():
    xhelp = xivelyHelper(FEED_ID,API_KEY,True)
    if not xhelp.get_datastream("test"):
        xhelp.create_datastream("test","test")

    while True:
        datapoint = random.random()
        xhelp.put_datapoint(datapoint)
        time.sleep(10)

main()
