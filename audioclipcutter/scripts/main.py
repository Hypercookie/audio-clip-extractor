# -*- coding: utf-8 -*-
import sys
import argparse
import glob
import shutil
import os

from audioclipcutter import AudioClipCutter

def cli():
    run(sys.argv[1:])

def run(args):
    ffmpegFilename = 'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg'

    parser = argparse.ArgumentParser(description='Audio Clip Cutter')
    parser.add_argument('--ffmpeg', default='')
    parser.add_argument('--output-dir', '-o', default='')
    parser.add_argument('--zip', '-z', action='store_true')
    parser.add_argument('--skip-path-lookup', action='store_true')
    parser.add_argument('files', nargs='*')

    r = parser.parse_args(args)

    # If the ffmpeg executable provided doesn't exist, look elsewhere (PATH)
    if not os.path.isfile(r.ffmpeg):
        if r.skip_path_lookup:
            r.ffmpeg = shutil.which(ffmpegFilename)

        if not r.ffmpeg:
            print("`%s` not found." % ffmpegFilename, file=sys.stderr)
            displayDownloadPage()
            sys.exit(1)

    files = None

    # If there's data being piped to stdin, consume it instead of processing r.files
    if checkIfThereIsDataBeingPipedToStdin():
        files = [os.path.abspath(f.strip()) for f in sys.stdin]
    else:
        files = r.files

    # Extract the clips
    for f in files:
        extractClips(os.path.abspath(f), r.ffmpeg, r.output_dir, r.zip)

    # Show help message when no files are provided
    if not files:
        print("Error: No audio files to process.", file=sys.stderr)
        parser.print_help()
        sys.exit(2)

def extractClips(filepath, ffmpeg, outputDir, zipOutput):
    specsFile = "%s.txt" % os.path.splitext(filepath)[0]

    if not os.path.isfile(specsFile):
        print("Error: `%s` not found." % specsFile, file=sys.stderr)
        exit(3)

    acc = AudioClipCutter(filepath, ffmpeg)
    acc.extractClips(specsFile, outputDir, zipOutput)

def checkIfThereIsDataBeingPipedToStdin():
    import sys
    import os
    from stat import S_ISFIFO

    if S_ISFIFO(os.fstat(0).st_mode):
        return True
    else:
        return False

def displayDownloadPage():
    message = 'FFMPEG can be downloaded at '

    if sys.platform == 'linux' or sys.platform == 'linux2':
        message += 'https://ffmpeg.org/download.html#build-linux'
    elif sys.platform ==  'darwin':
        message += 'http://evermeet.cx/ffmpeg/'
    elif sys.platform == 'win32':
        message += 'https://ffmpeg.zeranoe.com/builds/'

    print(message)
