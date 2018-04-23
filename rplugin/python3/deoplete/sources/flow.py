#!/usr/bin/env python
# coding: utf-8

import os
from .base import Base

CONFIG_FILE = '.flowconfig'

# Find closest configuration directory recursively.
# Borrows from https://github.com/steelsojka/deoplete-flow/pull/9/files
def find_config_dir(dir):
    if CONFIG_FILE in os.listdir(dir):
        return dir
    elif dir == '/':
        return None
    else:
        return find_config_dir(os.path.dirname(dir))

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'flow'
        self.mark = '[flow]'
        self.filetypes = ['javascript']
        self.min_pattern_length = 2
        self.rank = 10000
        self.input_pattern = '((?:\.|(?:,|:|->)\s+)\w*|\()'
        self._relatives = {}
        self._config_dirs = {}
        self.__completer = Completer(vim)

    def on_event(self, context):
        if context['event'] == 'BufRead' or context['event'] == 'BufNewFile':
            try:
                # Cache relative path from closest configuration directory.
                self.relative()
                pass
            except Exception:
                pass

    def get_complete_position(self, context):
        return self.__completer.determineCompletionPosition(context)

    def gather_candidates(self, context):
        rel, cfg_dir = self.relative()
        return self.__completer.find_candidates(context, rel, cfg_dir)

    def relative(self):
        filename = self.vim.eval("expand('%:p')")
        if filename in self._relatives:
            return (self._relatives[filename], self._config_dirs[filename])
        config_dir = find_config_dir(os.path.dirname(filename))
        if not config_dir:
            return (None, None)
        self._relatives[filename] = os.path.relpath(filename, config_dir)
        self._config_dirs[filename] = config_dir
        return (filename, config_dir)

class Completer(object):
    def __init__(self, vim):
        import re
        self.__vim = vim
        self.__completion_pattern = re.compile('\w*$')

    def get_flowbin(self):
        return self.__vim.vars['autocomplete_flow#flowbin']

    def determineCompletionPosition(self, context):
        result = self.__completion_pattern.search(context['input'])

        if result is None:
            return self.__vim.current.window.cursor.col

        return result.start()

    def abbreviateIfNeeded(self, text):
        return (text[:47] + '...') if len(text) > 50 else text

    def buildCompletionWord(self, json):

        # If not a function
        if not json['func_details']:
            return json['name']

        # If not using neosnippet
        if not self.__vim.vars.get('neosnippet#enable_completed_snippet'):
            if self.__vim.vars.get('autocomplete_flow#insert_paren_after_function'):
                return json['name'] + '('
            else:
                return json['name']

        def buildArgumentList(arg):
            index, paramDesc = arg
            return '<`' + str(index) + ':' + paramDesc['name'] + '`>'

        params = map(buildArgumentList, enumerate(json['func_details']['params']))
        return json['name'] + '(' + ', '.join(params) + ')'

    def find_candidates(self, context, relative, config_dir):
        from subprocess import Popen, PIPE
        import json

        line = str(self.__vim.current.window.cursor[0])
        column = str(self.__vim.current.window.cursor[1] + 1)
        if relative:
            command = [self.get_flowbin(), 'autocomplete', '--json', relative, line, column]
        else:
            command = [self.get_flowbin(), 'autocomplete', '--json', line, column]

        buf = '\n'.join(self.__vim.current.buffer[:])

        try:
            process = Popen(command, cwd=config_dir, stdout=PIPE, stdin=PIPE)
            command_results = process.communicate(input=str.encode(buf))[0]

            if process.returncode != 0:
                return []

            results = json.loads(command_results.decode('utf-8'))

            return [{
                'word': self.buildCompletionWord(x),
                'abbr': self.abbreviateIfNeeded(x['name']),
                'info': x['type'],
                'kind': self.abbreviateIfNeeded(x['type'])} for x in results['result']]
        except FileNotFoundError:
            pass
