import argparse


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to eyetracking data folder")
    parser.add_argument("--combined", type=str2bool, default=False, help="Create combined file too?")
    parser.add_argument("--separate", type=str2bool, default=True, help="Create saccade/blink/fixation/time files?")
    parser.add_argument("--BIDS", type=str2bool, default=False, help='Convert to BIDS?')
    args = parser.parse_args()
    return args
