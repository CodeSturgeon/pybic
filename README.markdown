# PyBIC
## Python Backup Integrity Checker
A small tool to help verify the integrity of backups.

## Basic usage
In it's simplist form, PyBIC will select 10 random files from a path and print them to stdout.  
`~$ pybic.py -s /path/to/files  
/path/to/files/file  
/path/to/files/some/sub/path/file  
/path/to/files/antoher/sub/path/file  
...`

## Advanced usage (md5 checking)
If a compare path is specified, PyBIC will use md5 to compare the selected files in the source and compare paths.
`~$ pybic.py -s /path/to/source -c /path/to/compare
/path/to/files/file
/path/to/files/some/sub/path/file
/path/to/files/antoher/sub/path/file
...`

## Complete command line options
These can be found by using '-h' on the script.
`~$ pybic.py -h`
