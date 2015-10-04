#!/usr/bin/env python3

import argparse
import json

from github import Github

def show_comments(args):
    print(args)

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    p_show_comments = subparsers.add_parser('sc')
    p_show_comments.add_argument('retain', nargs='*')
    p_show_comments.set_defaults(func=show_comments)

    return parser.parse_args()

def main():
    args = parse_args()

    with open('config.json') as config_file:
        config = json.load(config_file)

    g = Github(config['access_token'])
    repo = g.get_repo(config['repo'])
    print(list(repo.get_pulls()))

    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
