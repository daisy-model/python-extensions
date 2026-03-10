'''Test helper functions'''
import subprocess

def run_daisy(out_dir, dai_file):
    '''Run daisy'''
    args = [
        "daisy",
        "-q",
        "-d", out_dir,
        dai_file
    ]
    return subprocess.run(args, check=False)
