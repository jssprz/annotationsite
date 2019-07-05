import os
import sys
import hashlib
from argparse import ArgumentParser

os.environ['DJANGO_SETTINGS_MODULE'] = 'annotationsite.settings'
import django
django.setup()

from tweets.models import Tweet, TweetMedia


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


def find_and_remove_duplicated():
    index = {}
    dups = {}
    for m in TweetMedia.objects.all():
        # print(i)
        # path = os.path.join('H:', 'annotationsite/{}'.format(m.local_image.url))
        path = os.path.join('./media', m.local_image.url)
        if os.path.exists(path):
            file_hash = hashfile(path)
            if file_hash in index:
                indexed_media = index[file_hash]
                # update tweets that reference this media
                for tweet in Tweet.objects.filter(medias__id_str=m.id_str):
                    if indexed_media not in tweet.medias.all():
                        tweet.medias.add(indexed_media)

                # delete tweetmedia
                m.delete()

                # delete image file
                os.remove(path)

                dups[file_hash].append(path)
            else:
                index[file_hash] = m
                dups[file_hash] = [path]
        else:
            print('{} not found'.format(path))
    return dups


def printResults(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('Duplicates Found:')
        print('The following files are identical. The name could differ, but the content is identical')
        print('___________________')
        count = 0
        for result in results:
            count += len(result) - 1
            for subresult in result:
                print('\t\t%s' % subresult)
            print('___________________')
        print('total duplications: {}'.format(count))
    else:
        print('No duplicate files found.')


if __name__ == '__main__':
    parser = ArgumentParser('Determine duplicated images in folder')
    parser.add_argument("-source", type=str, choices=['folder', 'db'])
    parser.add_argument("-model", type=str, choices=['hash'],
                        help=" technique to be used to compare image files ", required=True)
    parser.add_argument("-folder", type=str, default='./media/tweet_medias',
                        help="path of the folder with image files", required=False)

    pargs = parser.parse_args()

    if pargs.source == 'folder':
        assert os.path.exists(pargs.folder), "{} folder doesn't exist".format(pargs.folder)
        printResults(findDup(pargs.folder))
    elif pargs.source == 'db':
        printResults(find_and_remove_duplicated())
