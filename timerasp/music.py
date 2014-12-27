'''


http://www.last.fm/music/+free-music-downloads/acoustic
'''
import os
import random
import hashlib
import subprocess
from datetime import datetime, timedelta

OUT_DIR = os.path.expanduser('~/video_archive/music/')


# a terrible ordered dict
FILES = {
    0:dict(
        artist = 'Podington Bear',
        title  = 'Starling',
        length = 60+45, # seconds
        url    = 'http://freemusicarchive.org/music/Podington_Bear/Solo_Instruments/Starling',
        audio  = 'http://freemusicarchive.org/music/download/be51c174a8a2ebcb5735aefc9bc573208f180e41',
    ),
    1:dict(
        artist = 'Kai Engel',
        title  = 'Moonlight Reprise',
        length = 3*60+1, # seconds
        url    = 'http://freemusicarchive.org/music/Kai_Engel/Irsens_Tale/Kai_Engel_-_Irsens_Tale_-_04_Moonlight_Reprise',
        audio  = 'http://freemusicarchive.org/music/download/84b48280791fbc4c81a355621aa1f13a8d15cd00',
    ),
    2:dict(  # TO REPLACE! single channel
        artist = 'Rolemusic',
        title  = 'The Pirate And The Dancer',
        length = 4*60+4, # seconds
        url    = 'http://freemusicarchive.org/music/Rolemusic/The_Pirate_And_The_Dancer/04_rolemusic_-_the_pirate_and_the_dancer',
        audio  = 'http://freemusicarchive.org/music/download/14102245609a0233dbf3d8b1552739ee3e00011a',
    ),
    3:dict(
        artist = 'deef',
        title = 'nostalgia of an ex-gangsta-rapper',
        length = 5*60+30, # seconds
        url = 'http://freemusicarchive.org/music/deef/Beat_Scene_Routine/4_-_deef_-_nostalgia_of_an_ex-gangsta-rapper',
        audio = 'http://freemusicarchive.org/music/download/ce5a59c22c7e1cbbc54e1d00f828c7ca8b0ed1e0',
    ),
    4:dict(
        artist = 'Peter Rudenko',
        title = 'Snowing',
        length = 2*60+22, # seconds
        url = 'http://freemusicarchive.org/music/Peter_Rudenko/15_Etudes/12_-_Peter_Rudenko_-_Snowing',
        audio = 'http://freemusicarchive.org/music/download/665fcd660419021138d22ddefee9609030006143',
    ),
    5:dict(
        artist = 'Percy Wenrich',
        title = 'The Smiler (1907, Zonophone Concert Band)',
        length = 2*60+27, # seconds
        url = 'http://freemusicarchive.org/music/Percy_Wenrich/Frog_Legs_Ragtime_Era_Favorites/02_-_percy_wenrich_-_the_smiler',
        audio = 'http://freemusicarchive.org/music/download/e6cd7ef9fdca57a9778a8b685066d8afa2f65d12',
    ),
    6:dict(
        artist = 'Project 5am',
        title = 'Yves',
        length = 7*60+27, # seconds
        url = 'http://freemusicarchive.org/music/Project_5am/5am_Wabi_Sabi/03_project_5am_-_yves',
        audio = 'http://freemusicarchive.org/music/download/fe55b17293f53bfea559e6fae82bbaf20a3c05d5',
    ),
    7:dict(
        artist = 'Project 5am',
        title = 'My Mind To Me, My Kingdom Is',
        length = 3*60+14, # seconds
        url = 'http://freemusicarchive.org/music/Project_5am/5am_Wabi_Sabi/04_project_5am_-_my_mind_to_me__my_kingdom_is',
        audio = 'http://freemusicarchive.org/music/download/96827f4cfd8561d1614c7f7004ce2a13836d0684',
    ),
}

TRACKS = [
    ['simple',[3]],
    ['odd',[0,3]],
    ['snow',[4,5]],
    # ['5am', [6]],
    # ['mind', [7,6]],
]

def call(cmd):
    print 'Running: {}'.format(cmd)
    subprocess.call(cmd, shell=True)
    

def get_filename(index, length=None):
    '''Hash the artist-title to get a simple filename'''
    key = '{} - {}'.format(FILES[index]['artist'], FILES[index]['title'])
    key_hash = hashlib.sha1(key).hexdigest()
    filename = 'audio_{key_hash}.mp3'
    if length:
        filename = 'audio_{key_hash}_{length:04d}.mp3'
    return os.path.join(OUT_DIR, filename.format(**locals()))

def get_music_filename(name, length):
    filename = 'music_{name}_{length:04d}.mp3'
    return os.path.join(OUT_DIR, filename.format(**locals()))
    

def get_track(index):
    '''Download the audio from the filename.'''
    
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    
    url = FILES[index]['audio']
    outfile = get_filename(index)
    
    if not os.path.exists(outfile):
        print 'Getting file: %s'%os.path.basename(outfile)
        call('wget -O {outfile} {url}'.format(**locals()))
    return outfile

def get_audio(index, length):
    '''Get te audio of a specific length with a fade.'''
    
    # ensure that the track exists
    filename = get_track(index)
    
    outfile = get_filename(index, length)
    if os.path.exists(outfile):
        print 'Have shortened file: %s'%os.path.basename(outfile)
        return outfile
    
    # it would be better to read in the length, but eh
    # cmd = 'sox {} 2>&1 -n stat | grep Length | cut -d : -f 2 | cut -f 1'.format(filename)
    # print subprocess.check_output(cmd, shell=True)
    if length > 10:
        call('sox {filename} {outfile} fade 5 {length} 5'.format(**locals()))
        return outfile
    else:
        call('sox {filename} {outfile} trim 0 {length}'.format(**locals()))
        # call('ln -s {filename} {outfile}'.format(**locals()))
        return outfile

def get_music(name, indicies, request_length):
    '''Get some length of music defaults to 5 minutes'''
    outfile = get_music_filename(name, request_length)
    if os.path.exists(outfile):
        print 'Music already created: %s'%os.path.basename(outfile)
        return outfile
    
    files = []
    lengths = []
    for index in indicies:
        
        file_length = FILES[index]['length']
        current_length = sum(lengths)
        if (current_length + file_length) > request_length:
            file_length = request_length - current_length
        if file_length <= 0:
            break
        
        filename = get_audio(index, file_length)
        files.append(filename)
        lengths.append(file_length)
        
        if current_length >= request_length:
            break
    
    if len(files) > 1:
        files = ' '.join(files)
        call('sox --combine concatenate {files} {outfile}'.format(**locals()))
        return outfile
    else:
        call('ln -s {files[0]} {outfile}'.format(**locals()))
        return outfile


def get_info(indicies):
    # fmt = '    * {artist} - {title}\n      > {url}\n'
    fmt = '  {artist} - {title}\n'
    out = ' Included Music:\n'
    for index in indicies:
        out += fmt.format(**FILES[index])
    return out.strip()

def get_date(date, request_length):
    random.seed(0)
    random.jumpahead(int((date-datetime(2014,12,25)).total_seconds()/86400))
    i = random.randint(0, len(TRACKS)-1)
    name, indicies = TRACKS[i]
    
    
    # only load when run build music
    # musicfile = get_music(name, indicies, request_length)
    musicfile = get_music_filename(name, request_length)
    musictext = get_info(indicies)
    info = dict(musicfile=musicfile,
                musictext=musictext,
                date=date,
                name=name,
                indicies=indicies,
                request_length=request_length)
    return info

def build(info):
    date = info['date']
    name = info['name']
    indicies = info['indicies']
    request_length = info['request_length']
    print 'Loading {name} {indicies} for date: {date}'.format(**locals())
    musicfile = get_music(name, indicies, request_length)
    return musicfile




if __name__ == '__main__':
    # get_track(2)
    
    # get_track(1)
    # get_audio(1, 5*60)
    # get_music('test', [0,3], 5*60)
    
    
    for name, indicies in TRACKS:
        if name == 'snow':
            get_music(name, indicies, 5*60)
    
    # now = datetime.now()
    # for i in range(10):
    #     # debug
    #     info = get_date(now + timedelta(days=i), 2)
    #     build(info)
    #     # Normal
    #     info = get_date(now + timedelta(days=i), 5*60)
    #     build(info)
        