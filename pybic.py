#!/usr/bin/env python

import os, os.path
import random

source_path = '/'

def pick_file(root_path):
    # Set [c]urrent [w]orking [p]ath
    cwp = root_path
    while not os.path.isfile(cwp):
        # Get list from cwp
        try:
            cwp_contents = os.listdir(cwp)
        except OSError:
            print 'resetting search due to perm error on %s'%cwp
            cwp = root_path
            continue
        # Pick one at random - must be dir, file, mount or link
        pick_path = ''
        while 1:
            # Empty dirs are a dead end
            if cwp_contents == []:
                # Reset the search and start again
                print 'No useable files in %s, resetting search'%cwp
                cwp = root_path
                break
            # Pick one directory entry at random
            pick = random.choice(cwp_contents)
            # Make a full path for the pick
            pick_path = os.path.join(cwp, pick)
            # Must be dir, file, mount or link
            if not (os.path.isdir(pick_path) or os.path.isfile(pick_path)
                        or os.path.ismount(pick_path)
                        or os.path.islink(pick_path)):
                # If not, we remove it from the options and pick again
                print 'removing unsueful "%s" (%s)'%(pick, pick_path)
                cwp_contents.remove(pick)
                continue
            # By this point we are happy with the pick and move on
            cwp = pick_path
            print cwp
            break
    return cwp

print pick_file(source_path)
