from rflint.common import GeneralRule, WARNING, ERROR, IGNORE
from rflint.parser import SettingTable, TestcaseTable
from rflint import RobotFactory, Keyword
from pathlib import PureWindowsPath
import re
import os
import sys
sys.path.append(os.path.dirname(__file__))
from utility import project_meta
import threading


def extract_max_same_path(files):
    dirs = [os.path.dirname(f) for f in files]
    if dirs == []:
        return ''
    chars = []
    for i in range(min([len(d) for d in dirs])):
        c = list(set([d[i] for d in dirs]))
        if len(c) == 1:
            chars.append(c[0])
        else:
            break
    return ''.join(chars)


def all_robot_files(path):
    ret = []
    p = PureWindowsPath(path)
    for root, _, files in os.walk(p.parents[0]):
        for f in files:
            if f.endswith('.txt') or f.endswith('.robot'):
                ret.append(os.path.join(root, f))
    return ret


def is_root_folder(path):
    try:
        if not os.path.isdir(path):
            return False
        if '.project' in [f.encode('cp950').decode() for f in os.listdir(path)]:
            return True
    except:
        if '.project' in [f.encode('utf-8').decode() for f in os.listdir(path)]:
            return True


def project_file(path):
    return '%s/.project' % project_root(path)


def project_root(path):
    if is_root_folder(path):
        return path
    return project_root(PureWindowsPath(path).parent)


def get_project_folder_files_def_keywords_map(path):
    return get_subfolder_files_def_keywords_map(project_file(PureWindowsPath(path).parent))


def get_subfolder_files_def_keywords_map(path):
    files = all_robot_files(path)
    file_keywords = dict()
    for f in files:
        file_keywords.setdefault(f, keywords(f))
    return file_keywords


def normalize_name(string):
    return string.replace(" ", "").replace("_", "").lower()


def keywords(file):
    rbfile = RobotFactory(file)
    ret = []
    for keyword in rbfile.walk(Keyword):
        ret.append(keyword)
    return ret


def same(keyword_def, keyword_use):
    """
    >>> same('Get Position', 'Get Position 1')
    False
    >>> same('Get Position', 'Get Position')
    True
    >>> same('Use Variable ${var1}', 'Use Variable 123')
    True
    >>> same('Use Variable 123', 'Use Variable ${var1}')
    True
    >>> same('Use Variable ${var1}', 'Use Variable ${var2}')
    True
    >>> same('Use Variable ${var1} hi', 'Use Variable 132')
    False
    >>> same('The Column ${customField} Was Set To Be Visible', 'The Column ${customField.fieldName} Was Set To Be Visible')
    True
    >>> same('The Column ${customField.fieldName} Was Set To Be Visible', 'The Column ${customField} Was Set To Be Visible')
    True
    >>> same('Action', '"*+,-./:;<="()')
    False
    >>> same('Action', '(')
    False
    >>> same('.', '.')
    True
    >>> same('Action', None)
    False
    """
    try:
        if keyword_def != keyword_use and (keyword_def == None or keyword_use == None):
            return False
        ndef = normalize_name(keyword_def)
        nuse = normalize_name(keyword_use)
        if ('{' in ndef and '}' in ndef) or ('{' in nuse and '}' in nuse):
            return re.match("^%s$" % re.sub(r'\\?[@$&]\\{[^\}]+\\}', r'.+', re.escape(ndef)), nuse) != None or re.match("^%s$" % re.sub(r'\\?[@$&]\\{[^\}]+\\}', r'.+', re.escape(nuse)), ndef) != None
        return ndef == nuse
    except:
        raise Exception((keyword_def, keyword_use))


metas = None
def get_metas(path):
    global metas
    if metas == None:
        metas = project_meta(path)
    return metas


class MoveKeyword(GeneralRule):

    severity = IGNORE

    def apply(self, rf_file):
        metas = get_metas(rf_file.path)
        current = next(filter(lambda x: x.source == rf_file.path, metas))
        for keyword, values in current.defs.items():
            used_metas = [meta for meta in metas if any([same(keyword, k) for k in meta.uses.keys()])]
            self_usage = any(same(keyword, used) for used in current.uses.keys())

            # Move the keyword to a file
            if len(used_metas) == 1 and not self_usage:
                self.report(rf_file, 'Move the keyword to file `%s`' % (os.path.relpath(used_metas[0].source, os.path.dirname(rf_file.path))), values['line'])

            # Move the keyword to a folder
            common_path = extract_max_same_path([meta.source for meta in used_metas])
            if len(used_metas) > 1 and os.path.normpath(common_path) != os.path.normpath(os.path.dirname(rf_file.path)) and os.path.isdir(common_path) and not self_usage:
                move = os.path.relpath(common_path, os.path.dirname(rf_file.path))
                if '..' not in move:
                    self.report(rf_file, 'Move the keyword to folder `%s\\keywords.txt`' % move, values['line'])


class UnusedKeyword(GeneralRule):

    severity = ERROR

    def apply(self, rf_file):
        rfMetas = get_metas(rf_file.path)
        current = next(filter(lambda meta: meta.source == rf_file.path, rfMetas))
        for keyword, values in current.defs.items():
            if current.is_test_data:
                if self.not_used(keyword, [current]):
                    self.report(rf_file, 'Unused Keyword', values['line'])
            else:
                if self.not_used(keyword, rfMetas):
                    self.report(rf_file, 'Unused Keyword', values['line'])

    def not_used(self, keyword, metas):
        for meta in metas:
            if any(same(keyword, used) for used in meta.uses.keys()):
                return False
        return True


class DuplicatedKeyword(GeneralRule):

    severity = WARNING

    def __init__(self, controller, severity=None):
        super().__init__(controller, severity=severity)
        self.file_with_keywords = None
        self.all_keywords = []
    
    def append_to_all_keywords_list(self):

        def remove_blank_line(keyword):
            keyword.rows = [row for row in keyword.rows if row.raw_text != '']

        for file, keywords in self.file_with_keywords.items():
            for keyword in keywords:
                remove_blank_line(keyword)
                self.all_keywords.append(keyword)

    def compare_with_same_implement_length(self, keywords, line_count):

        def set_duplicate_keyword_implement_message(duplicate_keywords):
            for keyword in duplicate_keywords:
                setattr(keyword, 'duplicate_implement', [other_keyword for other_keyword in duplicate_keywords if (other_keyword != keyword and other_keyword.parent.path != keyword.parent.path)])

        def separe_and_compare_line_by_line(to_be_compare_keywords, line_index):

            def lookahead(iterable):
                it = iter(iterable)
                last = next(it)
                for val in it:
                    yield last, False
                    last = val
                yield last, True
            
            def compare_or_set_message(keywords):
                if len(keywords) > 1:
                    if line_index + 1 == line_count:
                        set_duplicate_keyword_implement_message(keywords)
                    else:
                        separe_and_compare_line_by_line(keywords, line_index + 1)

            compare_list = []

            for keyword, is_last in lookahead(to_be_compare_keywords):
                if len(compare_list) == 0:
                    compare_list.append(keyword)
                elif keyword.rows[line_index].raw_text == compare_list[0].rows[line_index].raw_text:
                    compare_list.append(keyword)
                else:
                    compare_or_set_message(compare_list)
                    compare_list = [keyword]
                if is_last:
                    compare_or_set_message(compare_list)
        
        separe_and_compare_line_by_line(keywords, 0)

    def compare_with_same_keyword_name_length(self, keywords):

        def set_duplicate_keyword_name_message(duplicate_keywords):
            for keyword in duplicate_keywords:
                setattr(keyword, 'duplicate_name', [other_keyword for other_keyword in duplicate_keywords if (other_keyword != keyword and other_keyword.parent.path != keyword.parent.path)])

        compare_list = []
        current_duplicate_name = ''

        keywords = iter(keywords)
        while True:
            try:
                current_keyword = next(keywords)
                if current_keyword.name == current_duplicate_name:
                    compare_list.append(current_keyword)
                else:
                    if len(compare_list) > 1:
                        set_duplicate_keyword_name_message(compare_list)
                    compare_list = [current_keyword]
                    current_duplicate_name = current_keyword.name
            except StopIteration:
                if len(compare_list) > 1:
                    set_duplicate_keyword_name_message(compare_list)
                break

    def sorted_by_name_and_compare(self):
        all_keywords = sorted(self.all_keywords, key=lambda x:len(x.name))

        min_keywordNameLen = len(all_keywords[0].name)
        max_keywordNameLen = len(all_keywords[-1].name)

        threads = []
        for length in range(min_keywordNameLen, max_keywordNameLen+1):
            same_name_length_keywords = list(filter(lambda keyword: len(keyword.name)==length, all_keywords))
            if len(same_name_length_keywords) <= 1:
                continue
            same_name_length_keywords = sorted(same_name_length_keywords, key=lambda x:x.name)
            threads.append(threading.Thread(target=self.compare_with_same_keyword_name_length, args=(same_name_length_keywords,)))
            threads[len(threads)-1].start()
        
        for index in range(len(threads)):
            threads[index].join()

    def sorted_by_impl_length_and_compare(self):
        all_keywords = sorted(self.all_keywords, key=lambda x:len(x.rows))

        min_keywordImplLen = len(all_keywords[0].rows)
        max_keywordImplLen = len(all_keywords[-1].rows)

        threads = []
        for length in range(min_keywordImplLen, max_keywordImplLen+1):
            same_implement_length_keywords = list(filter(lambda x:len(x.rows)==length, all_keywords))
            if len(same_implement_length_keywords) <= 1:
                continue
            same_implement_length_keywords = sorted(same_implement_length_keywords, key=lambda x:[row.raw_text for row in x.rows])
            threads.append(threading.Thread(target=self.compare_with_same_implement_length, args=(same_implement_length_keywords, length,)))
            threads[len(threads)-1].start()
        
        for index in range(len(threads)):
            threads[index].join()

    def apply(self, rbfile):

        if self.file_with_keywords is None:

            self.file_with_keywords = get_project_folder_files_def_keywords_map(rbfile.path)
            self.append_to_all_keywords_list()
            
            threads = []
            threads.append(threading.Thread(target=self.sorted_by_name_and_compare))
            threads.append(threading.Thread(target=self.sorted_by_impl_length_and_compare))

            threads[0].start()
            threads[1].start()

            for index in range(len(threads)):
                threads[index].join()

        for keyword in self.file_with_keywords[rbfile.path]:
            if hasattr(keyword, 'duplicate_implement'):
                if hasattr(keyword, 'duplicate_name'):
                    for duplicate_keyword in keyword.duplicate_implement:
                        if duplicate_keyword in keyword.duplicate_name:
                            self.report(keyword, 'Duplicated Keyword (name and impl): %s:%d' % (os.path.relpath(duplicate_keyword.parent.path, os.path.dirname(rbfile.path)), duplicate_keyword.linenumber), keyword.linenumber)
                        else:
                            self.report(keyword, 'Duplicated Keyword (impl): %s:%d [%s]' % (os.path.relpath(duplicate_keyword.parent.path, os.path.dirname(rbfile.path)), duplicate_keyword.linenumber, duplicate_keyword.name), keyword.linenumber)
                    for duplicate_keyword in keyword.duplicate_name:
                        if duplicate_keyword not in keyword.duplicate_implement:
                            self.report(keyword, 'Duplicated Keyword (name): %s:%d' % (os.path.relpath(duplicate_keyword.parent.path, os.path.dirname(rbfile.path)), duplicate_keyword.linenumber), keyword.linenumber)
                else:
                    for duplicate_keyword in keyword.duplicate_implement:
                        self.report(keyword, 'Duplicated Keyword (impl): %s:%d [%s]' % (os.path.relpath(duplicate_keyword.parent.path, os.path.dirname(rbfile.path)), duplicate_keyword.linenumber, duplicate_keyword.name), keyword.linenumber)
            elif hasattr(keyword, 'duplicate_name'):
                for duplicate_keyword in keyword.duplicate_name:
                    self.report(keyword, 'Duplicated Keyword (name): %s:%d' % (os.path.relpath(duplicate_keyword.parent.path, os.path.dirname(rbfile.path)), duplicate_keyword.linenumber), keyword.linenumber)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
