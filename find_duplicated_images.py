import os
import sys
import hashlib

from argparse import ArgumentParser


def hashfile(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def findDup(parentFolder):
    # Dups in format {hash:[names]}
    dups = {}
    for dirName, subdirs, fileList in os.walk(parentFolder):
        print('Scanning %s...' % dirName)
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            # Calculate hash
            file_hash = hashfile(path)
            # Add or append the file path
            if file_hash in dups:
                dups[file_hash].append(path)
            else:
                dups[file_hash] = [path]
    return dups


def printResults(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('Duplicates Found:')
        print('The following files are identical. The name could differ, but the content is identical')
        print('___________________')
        for result in results:
            for subresult in result:
                print('\t\t%s' % subresult)
            print('___________________')

    else:
        print('No duplicate files found.')


if __name__ == '__main__':
    parser = ArgumentParser('Determine duplicated images in folder')
    parser.add_argument("-model", type=str, choices=['hash'],
                        help=" tachnique to be used to compare image files ", required=True)
    parser.add_argument("-folder", type=str, default='./media/tweet_medias',
                        help="path of the folder with image files", required=False)

    pargs = parser.parse_args()

    assert os.path.exists(pargs.folder), "{} folder doesn't exist"

    printResults(findDup(pargs.folder))
