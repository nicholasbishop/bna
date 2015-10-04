#!/usr/bin/env python3

import argparse
import json
import subprocess

from github import Github

class GithubBackend:
    def __init__(self, config):
        self._config = dict(config)
        self._patch = None

    def patch(self):
        if self._patch is None:
            rapi = Github(self._config['access_token'])
            repo = rapi.get_repo(self._config['repo'])
            # TODO(nicholasbishop): placeholder PR
            self._patch = repo.get_pull(1)
        return self._patch

    def create_comment(self, args):
        if args.location and args.message:
            location = args.location.split(':')
            commit = self.patch().get_commits()[0]
            self.patch().create_comment(body=args.message,
                                        commit_id=commit,
                                        path=location[0],
                                        position=int(location[1]))
        else:
            raise NotImplementedError()

    def show_comments(self, args):
        for comment in self.patch().get_comments():
            print('{}:{}: {}'.format(comment.path,
                                     comment.position,
                                     comment.body))

def parse_args(backend):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    p_show_comments = subparsers.add_parser('cc')
    p_show_comments.add_argument('location', nargs='?')
    p_show_comments.add_argument('message', nargs='?')
    p_show_comments.set_defaults(func=backend.create_comment)

    p_show_comments = subparsers.add_parser('sc')
    p_show_comments.add_argument('retain', nargs='*')
    p_show_comments.set_defaults(func=backend.show_comments)

    return parser.parse_args()

def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    backend = GithubBackend(config)
    args = parse_args(backend)

    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
