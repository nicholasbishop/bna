#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
from tempfile import mkstemp

from github import Github

def edit_message():
    editor = os.environ['EDITOR']
    message_file, message_path = mkstemp()
    try:
        os.close(message_file)
        cmd = (editor, message_path)
        subprocess.check_call(cmd)
        with open(message_path) as message_file:
            return message_file.read()
    finally:
        os.unlink(message_path)

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
        location = args.location
        if not location:
            raise NotImplementedError()

        message = args.message
        if not message:
            message = edit_message()

        commit = self.patch().get_commits()[0]
        self.patch().create_comment(body=message,
                                    commit_id=commit,
                                    path=location.path,
                                    position=location.line_no)

    def show_comments(self, args):
        for index, comment in enumerate(self.patch().get_comments()):
            print('{}) {}:{}: {}'.format(index,
                                         comment.path,
                                         comment.position,
                                         comment.body))


class Location:
    def __init__(self, path, line_no):
        self.path = path
        self.line_no = int(line_no)

    @staticmethod
    def parse(string):
        try:
            return Location(*string.split(':'))
        except AttributeError:
            return None


class LocationAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, Location.parse(values))


def parse_args(backend):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    p_show_comments = subparsers.add_parser('cc')
    p_show_comments.add_argument('location', nargs='?',
                                 action=LocationAction)
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
