#!/usr/bin/env python

'''


http://www.last.fm/music/+free-music-downloads/acoustic
'''
import os
import sys
import random
import hashlib
import subprocess
from datetime import datetime, timedelta

OUT_DIR = os.path.expanduser('~/video_archive/music/')


# # a terrible ordered dict
# FILES = {
#     0:dict(
#         artist = 'Podington Bear',
#         title  = 'Starling',
#         length = 60+45, # seconds
#         url    = 'http://freemusicarchive.org/music/Podington_Bear/Solo_Instruments/Starling',
#         audio  = 'http://freemusicarchive.org/music/download/be51c174a8a2ebcb5735aefc9bc573208f180e41',
#     ),
#     1:dict(
#         artist = 'Kai Engel',
#         title  = 'Moonlight Reprise',
#         length = 3*60+1, # seconds
#         url    = 'http://freemusicarchive.org/music/Kai_Engel/Irsens_Tale/Kai_Engel_-_Irsens_Tale_-_04_Moonlight_Reprise',
#         audio  = 'http://freemusicarchive.org/music/download/84b48280791fbc4c81a355621aa1f13a8d15cd00',
#     ),
#     2:dict(  # TO REPLACE! single channel
#         artist = 'Rolemusic',
#         title  = 'The Pirate And The Dancer',
#         length = 4*60+4, # seconds
#         url    = 'http://freemusicarchive.org/music/Rolemusic/The_Pirate_And_The_Dancer/04_rolemusic_-_the_pirate_and_the_dancer',
#         audio  = 'http://freemusicarchive.org/music/download/14102245609a0233dbf3d8b1552739ee3e00011a',
#     ),
#     3:dict(
#         artist = 'deef',
#         title = 'nostalgia of an ex-gangsta-rapper',
#         length = 5*60+30, # seconds
#         url = 'http://freemusicarchive.org/music/deef/Beat_Scene_Routine/4_-_deef_-_nostalgia_of_an_ex-gangsta-rapper',
#         audio = 'http://freemusicarchive.org/music/download/ce5a59c22c7e1cbbc54e1d00f828c7ca8b0ed1e0',
#     ),
#     4:dict(
#         artist = 'Peter Rudenko',
#         title = 'Snowing',
#         length = 2*60+22, # seconds
#         url = 'http://freemusicarchive.org/music/Peter_Rudenko/15_Etudes/12_-_Peter_Rudenko_-_Snowing',
#         audio = 'http://freemusicarchive.org/music/download/665fcd660419021138d22ddefee9609030006143',
#     ),
#     5:dict(
#         artist = 'Percy Wenrich',
#         title = 'The Smiler (1907, Zonophone Concert Band)',
#         length = 2*60+27, # seconds
#         url = 'http://freemusicarchive.org/music/Percy_Wenrich/Frog_Legs_Ragtime_Era_Favorites/02_-_percy_wenrich_-_the_smiler',
#         audio = 'http://freemusicarchive.org/music/download/e6cd7ef9fdca57a9778a8b685066d8afa2f65d12',
#     ),
#     6:dict(
#         artist = 'Project 5am',
#         title = 'Yves',
#         length = 7*60+27, # seconds
#         url = 'http://freemusicarchive.org/music/Project_5am/5am_Wabi_Sabi/03_project_5am_-_yves',
#         audio = 'http://freemusicarchive.org/music/download/fe55b17293f53bfea559e6fae82bbaf20a3c05d5',
#     ),
#     7:dict(
#         artist = 'Project 5am',
#         title = 'My Mind To Me, My Kingdom Is',
#         length = 3*60+14, # seconds
#         url = 'http://freemusicarchive.org/music/Project_5am/5am_Wabi_Sabi/04_project_5am_-_my_mind_to_me__my_kingdom_is',
#         audio = 'http://freemusicarchive.org/music/download/96827f4cfd8561d1614c7f7004ce2a13836d0684',
#     ),
# }
#
# TRACKS = [
#     ['simple',[3]],
#     ['odd',[0,3]],
#     ['snow',[4,5]],
#     # ['5am', [6]],
#     # ['mind', [7,6]],
# ]
#
# def call(cmd):
#     print 'Running: {}'.format(cmd)
#     subprocess.call(cmd, shell=True)
#
#
# def get_filename(index, length=None):
#     '''Hash the artist-title to get a simple filename'''
#     key = '{} - {}'.format(FILES[index]['artist'], FILES[index]['title'])
#     key_hash = hashlib.sha1(key).hexdigest()
#     filename = 'audio_{key_hash}.mp3'
#     if length:
#         filename = 'audio_{key_hash}_{length:04d}.mp3'
#     return os.path.join(OUT_DIR, filename.format(**locals()))
#
# def get_music_filename(name, length):
#     filename = 'music_{name}_{length:04d}.mp3'
#     return os.path.join(OUT_DIR, filename.format(**locals()))
#
#
# def get_track(index):
#     '''Download the audio from the filename.'''
#
#     if not os.path.exists(OUT_DIR):
#         os.makedirs(OUT_DIR)
#
#     url = FILES[index]['audio']
#     outfile = get_filename(index)
#
#     if not os.path.exists(outfile):
#         print 'Getting file: %s'%os.path.basename(outfile)
#         call('wget -O {outfile} {url}'.format(**locals()))
#     return outfile
#
# def get_audio(index, length):
#     '''Get te audio of a specific length with a fade.'''
#
#     # ensure that the track exists
#     filename = get_track(index)
#
#     outfile = get_filename(index, length)
#     if os.path.exists(outfile):
#         print 'Have shortened file: %s'%os.path.basename(outfile)
#         return outfile
#
#     # it would be better to read in the length, but eh
#     # cmd = 'sox {} 2>&1 -n stat | grep Length | cut -d : -f 2 | cut -f 1'.format(filename)
#     # print subprocess.check_output(cmd, shell=True)
#     if length > 10:
#         call('sox {filename} {outfile} fade 5 {length} 5'.format(**locals()))
#         return outfile
#     else:
#         call('sox {filename} {outfile} trim 0 {length}'.format(**locals()))
#         # call('ln -s {filename} {outfile}'.format(**locals()))
#         return outfile
#
# def get_music(name, indicies, request_length):
#     '''Get some length of music defaults to 5 minutes'''
#     outfile = get_music_filename(name, request_length)
#     if os.path.exists(outfile):
#         print 'Music already created: %s'%os.path.basename(outfile)
#         return outfile
#
#     files = []
#     lengths = []
#     for index in indicies:
#
#         file_length = FILES[index]['length']
#         current_length = sum(lengths)
#         if (current_length + file_length) > request_length:
#             file_length = request_length - current_length
#         if file_length <= 0:
#             break
#
#         filename = get_audio(index, file_length)
#         files.append(filename)
#         lengths.append(file_length)
#
#         if current_length >= request_length:
#             break
#
#     if len(files) > 1:
#         files = ' '.join(files)
#         call('sox --combine concatenate {files} {outfile}'.format(**locals()))
#         return outfile
#     else:
#         call('ln -s {files[0]} {outfile}'.format(**locals()))
#         return outfile
#
#
# def get_info(indicies):
#     # fmt = '    * {artist} - {title}\n      > {url}\n'
#     fmt = '  {artist} - {title}\n'
#     out = ' Included Music:\n'
#     for index in indicies:
#         out += fmt.format(**FILES[index])
#     return out.strip()
#
# def get_date(date, request_length):
#     random.seed(0)
#     random.jumpahead(int((date-datetime(2014,12,25)).total_seconds()/86400))
#     i = random.randint(0, len(TRACKS)-1)
#     name, indicies = TRACKS[i]
#
#
#     # only load when run build music
#     # musicfile = get_music(name, indicies, request_length)
#     musicfile = get_music_filename(name, request_length)
#     musictext = get_info(indicies)
#     info = dict(musicfile=musicfile,
#                 musictext=musictext,
#                 date=date,
#                 name=name,
#                 indicies=indicies,
#                 request_length=request_length)
#     return info
#
# def build(info):
#     date = info['date']
#     name = info['name']
#     indicies = info['indicies']
#     request_length = info['request_length']
#     print 'Loading {name} {indicies} for date: {date}'.format(**locals())
#     musicfile = get_music(name, indicies, request_length)
#     return musicfile





import json
import glob

import tempfile

from pprint import pprint

try:
    import eyed3
    import audioread
except:
    # print 'eyed3 and audioread only required for processing of music'
    pass

# where to save the files before the pi
TEMP_DIR = os.path.expanduser('~/tmp/music/output/')
PI_DIR = os.path.expanduser('~/video_archive/music')
if os.path.exists(PI_DIR):
    TEMP_DIR = PI_DIR

JSON_FILE = os.path.join(TEMP_DIR, 'tracksets.json')
README_FILE = os.path.join(TEMP_DIR, 'readme.txt')


def check_call(cmd):
    print '  Running: {}'.format(cmd)
    subprocess.check_call(cmd, shell=True)


def get_info(filename):
    '''Get the information of the track'''
    audiofile = eyed3.load(filename)
    audio = audioread.audio_open(filename)
    info = dict(
        artist = audiofile.tag.artist,
        title = audiofile.tag.title,
        channels = audio.channels,
        samplerate = audio.samplerate,
        duration = audio.duration,
        filename = filename,
    )
    return info

def cut_file(filename, playtime, fadelength):
    '''Cut the file with some fade at the end
    add a 1 sec intro fade just in case
    '''
    if (fadelength > 0) and (playtime > (fadelength+1)):
        options = 'fade 1 {playtime} {fadelength}'.format(**locals())
    else:
        options = 'trim 0 {playtime}'.format(**locals())
    
    f  = tempfile.NamedTemporaryFile('w', prefix='timerasp_', suffix='.mp3')
    outfile = f.name
    cmd = 'sox "{filename}" "{outfile}" {options}'.format(**locals())
    check_call(cmd)
    return f

def get_concatenate_fileprop(tracks):
    '''Return the filename, key (artist-title series), and hash for a concatenated 
    trackset'''
    key = u' ;; '.join([u'{} - {}'.format(t['artist'], t['title']) for t in tracks])
    key_hash = hashlib.sha1(key.encode('utf8')).hexdigest()
    outfile = os.path.join(TEMP_DIR, 'trackset_{}.mp3'.format(key_hash))
    return outfile, key, key_hash


def concatenate_files(files, tracks, length, fadelength):
    '''Combine a set of files/tracks into a singlefile 
    returns a dict of its properties.'''
    outfile, outnames, outhash = get_concatenate_fileprop(tracks)
    
    if os.path.exists(outfile):
        print u'File already exists:\n  {}\n  {}'.format(outfile, outnames)
    else:
        # carve up files if needed
        for tmp in files:
            if not isinstance(tmp, str):
                filename, playtime = tmp
                cutfile = cut_file(filename, playtime, fadelength)
                ifiles = files.index(tmp)
                files[ifiles] = cutfile.name
        
        # unicode strings here breaks things.  wtf!
        safefiles = ' '.join(['"{}"'.format(f) for f in files])
        if len(files) > 1:
            # need to combine them
            cmd = 'sox --combine concatenate {safefiles} {outfile}'.format(**locals())
        else:
            # just move to the right location
            cmd = 'rsync -rav {safefiles} {outfile}'.format(**locals())
        check_call(cmd)
    
    # clean up tmp files
    # for cutfile in cleanup:
    #     cutfile.close()
    
    info = dict(
        filekey = outnames,
        basename = os.path.basename(outfile),
        filehash = outhash,
        nicename = outnames.replace(';;','\n'),
        length = length,
    )
    return info
    
    
    

def build_trackset(tracks, length, fadelength=None):
    '''Combine the tracks into a nice auto trackset.
    length in seconds
    fadelength in seconds [10]'''
    if fadelength is None: fadelength = 10
    
    currentlength = 0
    files = []
    cleanup = []
    for track in tracks:
        currentlength += track['duration']
        
        if currentlength < length:
            files.append(track['filename'])
        else:
            # above current length so cut and fade
            playtime = length - (currentlength - track['duration'])
            files.append((track['filename'], playtime))
            # print ' !! CUTTING: {} {}'.format(track['filename'], playtime)
    
    # combine files into a single mp3
    info = concatenate_files(files, tracks, length, fadelength)
    
    return info

def save_tracksets_json(tracksets):
    '''update the json with information from the tracksets
    update the flat text file for simplicity
    '''
    
    try:
        data = json.load(open(JSON_FILE,'r'))
    except Exception as e:
        print u'Failed to load trackset json: {}'.format(e)
        if raw_input('is this ok? [y/n]').lower() != 'y':
            raise e
        data = []
    
    hashes = [d['filehash'] for d in data]
    for trackset in tracksets:
        if trackset['filehash'] not in hashes:
            data.append(trackset)
    print '---track info---'
    pprint(data)
    print '--- end track info---'
    if raw_input('save? [y/n]').lower() == 'y':
        json.dump(data, open(JSON_FILE,'w'), indent=2)
    

def save_tracksets_readme(tracksets):
    # make a nice readme file too
    try:
        # make sure there is a file there
        if not os.path.exists(README_FILE):
            # touch file
            with open(README_FILE, 'w') as f:
                f.write('# FILENAME :: artists - tracks')
        
        # get the current file -- rw breaks things so here this is.
        with open(README_FILE, 'r') as f:
            tmp = f.readlines()
        
        # write out the data
        with open(README_FILE, 'a') as f:
            filenames = [t.split(' :: ')[0] for t in tmp if ' :: ' in t]
            for trackset in tracksets:
                if trackset['basename'] not in filenames:
                    f.write(u'\n{basename} :: {filekey}'.format(**trackset).encode('utf8'))
    except Exception as e:
        print 'Failed to adjust readme_file: {}'.format(e)
        raise e

def get_directory(directory, length=None, fadelength=None):
    '''Build a nice json + music files from a directory
    length -- length of composition [s]
    fadelength -- length to fade last song [s]
    # for each file in a directory
    #   Grab info of the file (artist, title, length)
    # for each track:
    #   accumulate enough to make length
    # for each trackset
    #   fade the last song
    #   combine
    
    '''
    if length is None: length = 5 * 60
    
    
    tracks = []
    for filename in glob.glob(os.path.join(directory, '*.mp3')):
        info = get_info(filename)
        
        # this breaks SOX so lets go with stereo -- TODO upmix
        if info['channels'] != 2:
            continue
        
        tracks.append(info)
    
    # combine depending on length
    currentlength = 0
    tracksets = []
    # so sexy index math here... not sure how to pythonify this
    for i in range(len(tracks)):
        for j in range(i, len(tracks)):
            print currentlength, 
            currentlength += tracks[j]['duration']
            
            if currentlength > length:
                tmp = '\n   '.join([t['title']+' {:0.2f}'.format(t['duration']) 
                                        for t in tracks[i:j+1]])
                print u'----\n{}\n   {}'.format(currentlength,tmp)
                tracksets.append(build_trackset(tracks[i:j+1], length, fadelength))
                currentlength = 0
                break
        
        # if currentlength > length:
        #
        #
        # if currentlength < length:
        #     currentlength += info['duration']
        #     tracks.append(info)
        #
        # print currentlength
        # if currentlength > length:
        #     # have enough music to build the trackset
        #     # tracksets.append(build_trackset(tracks, length, fadelength))
        #     print '----\n   {}'.format([[t['title'],t['duration']] for t in tracks])
        #
        #     # most likely the last song(s) are shortened so include
        #     # them for other tracksets
        #     if len(tracks) > 1:
        #         tracks = tracks[1:]
        #         currentlength = sum([i['duration'] for i in tracks])
        #     else:
        #         tracks = []
        #         currentlength = 0
        
    
    # save the created tracksets to disk
    save_tracksets_json(tracksets)
    save_tracksets_readme(tracksets)



def get_random_trackset(date, length):
    '''Try to grab a random song for the date today
    randomizes by current day -- NOT SECURE, just simple '''
    random.seed(0)
    random.jumpahead(int((date-datetime(2014,12,25)).total_seconds()/86400))
    tracksets = json.load(open(JSON_FILE,'r'))
    
    while True:
        i = random.randint(0, len(tracksets)-1)
        trackset = tracksets[i]
        musicfile = os.path.join(TEMP_DIR, trackset['basename'])
        if os.path.exists(musicfile):
            break
    
    musictext = '[Included Music]' + ' '.join(['\n  '+t.strip() for t in trackset['nicename'].splitlines()])

    info = dict(musicfile=musicfile,
                musictext=musictext.encode('utf8'), # this might be bad
                index=i,
                date=date,
                length=length)
    return info

if __name__ == '__main__':
    
    ### VERSION 2 tests
    # cut_file('test', 10,2)
    
    if len(sys.argv) > 1:
        get_directory(sys.argv[1])
    else:
        now = datetime.now()
        print now
        for i in range(20):
            print
            print i
            info = get_random_trackset(now + timedelta(days=i), 300)
            pprint(info)
            print info['musictext']
    
    
    
    #### VERSION 1 tests
    
    # get_track(2)
    
    # get_track(1)
    # get_audio(1, 5*60)
    # get_music('test', [0,3], 5*60)
    
    
    # for name, indicies in TRACKS:
    #     if name == 'snow':
    #         get_music(name, indicies, 5*60)
    
    # now = datetime.now()
    # for i in range(10):
    #     # debug
    #     info = get_date(now + timedelta(days=i), 2)
    #     build(info)
    #     # Normal
    #     info = get_date(now + timedelta(days=i), 5*60)
    #     build(info)
        