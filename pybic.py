#!/usr/bin/env python

import os, os.path
import sys
import random
import logging
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-s', '--source-path', dest='source_path',
        help='The source path')
parser.add_option('-n', '--number-of-files', dest='filenumber', type='int',
        help='Number of files to pick')
parser.add_option('-v', '--verbose', action='store_const', const=20,
        dest='out_lvl', help='Get extra information on the picking')
parser.add_option('-d', '--debug', action='store_const', const=0,
        dest='out_lvl', help='Dump all debugging information')
parser.set_defaults(out_lvl=30, filenumber=10, source_path='/')
(options, args) = parser.parse_args()

# Setup logging for commandline use
log = logging.getLogger()
# Base logger should not filter on level
log.setLevel(logging.NOTSET)

class MaxFilter(logging.Filter):
    '''Small logging filter to block logging.ERROR level or above.
    Used to seperate stdout and stderr output
    '''
    def filter(self, rec):
        if rec.levelno < logging.ERROR:
            return 1
        else:
            return 0

# put info+warn to stdout
stdout = logging.StreamHandler(sys.stdout)
stdout.setLevel(options.out_lvl)
stdout_fmt = logging.Formatter('%(name)-9s : %(levelname)s %(message)s')
stdout.setFormatter(stdout_fmt)
stdout.addFilter(MaxFilter())
log.addHandler(stdout)

# put err+crit to stderr
stderr = logging.StreamHandler(sys.stderr)
stderr.setLevel(logging.ERROR)
stderr_fmt = logging.Formatter('%(levelname)s! %(message)s [%(name)s]')
stderr.setFormatter(stderr_fmt)
log.addHandler(stderr)

def pick_file(root_path):
    log = logging.getLogger('pick_file')
    # Set [c]urrent [w]orking [p]ath
    cwp = root_path
    while not os.path.isfile(cwp):
        # Get list from cwp
        try:
            cwp_contents = os.listdir(cwp)
        except OSError:
            log.info('resetting search due to perm error on %s'%cwp)
            cwp = root_path
            continue
        # Pick one at random - must be dir, file, mount or link
        while 1:
            # Empty dirs are a dead end
            if cwp_contents == []:
                # Reset the search and start again
                log.info('No useable files in %s, resetting search'%cwp)
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
                log.info('avoiding unuseful %s'%pick_path)
                cwp_contents.remove(pick)
                continue
            # By this point we are happy with the pick and move on
            cwp = pick_path
            log.info(cwp)
            break
    return cwp

picks = []
pick = ''
while len(picks) < options.filenumber:
    pick = pick_file(options.source_path)
    if pick not in picks:
        picks.append(pick)
        print pick
