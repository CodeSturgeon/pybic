#!/usr/bin/env python

import os, os.path
import sys
import random
import logging
from optparse import OptionParser

class MaxFilter(logging.Filter):
    '''Small logging filter to block logging.ERROR level or above.
    Used to seperate stdout and stderr output
    '''
    def filter(self, rec):
        '''Only allow records under ERROR'''
        if rec.levelno < logging.ERROR:
            return 1
        else:
            return 0

def pick_file(root_path, one_filesystem=False):
    '''Given a path, select a file at random'''
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

            # On to see if we can use the pick...
            # If we are in one-filesystem mode we skip on mounts
            if os.path.ismount(pick_path):
                if one_filesystem:
                    log.info('avoinding mount point %s'%pick_path)
                    cwp_contents.remove(pick)
                    continue
            # Must be dir, file, or link tp be usable
            elif not (os.path.isdir(pick_path) or os.path.isfile(pick_path)
                        or os.path.islink(pick_path)):
                # If not, we remove it from the options and pick again
                log.info('avoiding unuseful %s'%pick_path)
                cwp_contents.remove(pick)
                continue
            # By this point we are happy with the pick and move on
            cwp = pick_path
            log.info('picking %s'%cwp)
            break
    return cwp

def compare(file_a, file_b):
    '''Compare two files for consistancy'''
    print file_b
    return True

def main():
    '''Standard main loop'''
    parser = OptionParser()
    parser.add_option('-s', '--search-path', dest='search_path',
            help='The search path to pick files from')
    parser.add_option('-c', '--compare-path', dest='compare_path',
            help='The mirrored source path to be checked for consistancy')
    parser.add_option('-n', '--number-of-files', dest='filenumber', type='int',
            help='Number of files to pick')
    parser.add_option('-o', '--one-filesystem', dest='one_filesystem',
            action='store_true', help='Do not follow mount points')
    parser.add_option('-f', '--follow-mounts', dest='one_filesystem',
            action='store_false', help='Do follow mount points')
    parser.add_option('-v', '--verbose', action='store_const', const=20,
            dest='stdout_logLevel', help='Get extra information on the picking')
    parser.add_option('-V', '--debug', action='store_const', const=0,
            dest='stdout_logLevel', help='Dump all debugging information')
    parser.set_defaults(stdout_logLevel=30, filenumber=10, search_path='/',
            one_filesystem=True)
    (options, args) = parser.parse_args()

    # Setup logging for commandline use
    log = logging.getLogger()
    # Base logger should not filter on level
    log.setLevel(logging.NOTSET)
    # put info+warn to stdout
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(options.stdout_logLevel)
    stdout_fmt = logging.Formatter('%(name)-9s : %(levelname)s %(message)s')
    stdout.setFormatter(stdout_fmt)
    stdout.addFilter(MaxFilter())
    log.addHandler(stdout)

    # put err+crit to stderr
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(logging.ERROR)
    stderr_fmt = logging.Formatter('!!%(levelname)s!! %(message)s [%(name)s]')
    stderr.setFormatter(stderr_fmt)
    log.addHandler(stderr)

    picks = []
    pick = ''
    log.debug('Looking for %i files'%options.filenumber)
    search_path = os.path.normpath(options.search_path)
    while len(picks) < options.filenumber:
        pick = pick_file(search_path, options.one_filesystem)
        if pick not in picks:
            picks.append(pick)
            print pick
            if options.compare_path is not None:
                compare_path = os.path.join(options.compare_path,
                        os.path.normpath(pick[len(search_path)+1:])
                        )
                if not compare(pick, compare_path):
                    print 'files do not match :('
                    sys.exit(2)
        else:
            log.info('Picked duplicate %s, trying again'%pick)

if __name__ == "__main__":
    main()
