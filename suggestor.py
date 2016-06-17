import itertools
import logging
import re

from argparse import ArgumentParser
from copy import copy
from glob import glob
from nltk.util import ngrams
from nltk.metrics.distance import edit_distance
from ConfigParser import SafeConfigParser

logging.basicConfig(format='%(message)s', level=logging.INFO)


class Domainer:
    """
    Domain names generator
    """

    def __init__(self):
        # Parse config
        self.local_domains = 'domains/'

    def parse_cl(self):
        """Parse commands from the command line"""
        parser = ArgumentParser(description='Domain names generator')
        parser.add_argument('-l', '--length', metavar='Length', type=int,
                            default=0, help='Max domain length with zone')
        parser.add_argument('-k', '--keyword', metavar='Keyword', type=str,
                            help='Input data: "word1 word2"')
        parser.add_argument('-n', '--ngrams', metavar='Grams', type=int, default=0,
                            help='Ngram length')
        parser.add_argument('-o', '--output', metavar='Writefile', default=False,
                            help='Output file')
        parser.add_argument('-f', '--file', metavar='Filename', default=False,
                            help='Read input data from the file')
        parser.add_argument('-z', '--zone', metavar='Zone', default='com',
                            help='Domain zones separated with comma')
        return parser

    def cli_process(self):
        """Process arguments from the cl"""
        # Parse args from the cl
        parser = self.parse_cl()
        args = parser.parse_args()

        if args.file:
            domains = []
            for keyword in open(args.file):
                # Gen domains
                domains.extend(self.gen_domains(keyword,
                    args.ngrams, args.zone, args.length, sort=True))
            logging.info(domains)
            # Save to file
            if args.output:
                with open(args.output, 'w+') as f:
                    f.write('\n'.join(domains))

        elif args.keyword:
            # Gen domains
            domains = self.gen_domains(args.keyword,
                    args.ngrams, args.zone, args.length, sort=True)
            logging.info(domains)
            # Save to file
            if args.output:
                with open(args.output, 'w+') as f:
                    f.write('\n'.join(domains))

        else:
            parser.print_help()

    def gen_domains(self, keyword, grams_length=0,
            zone='com', length=0, sort=False):
        """
        Search domains by words

        :param sort: Sort names by Levenshtein
        :rtype: list
        :return: list of domains
        """
        def check_lengh(line):
            if len(line) < length + len(zone):
                return True

        domains = []
        grams_list = []
        files = glob('{}/*.txt'.format(self.local_domains.rstrip('/')))

        # Generate ngrams list
        for word in keyword.split():
            if grams_length:
                grams = ngrams(list(word.strip()), grams_length)
                for gram in grams:
                    grams_list.append(''.join(gram))
            else:
                grams_list.append(word.strip())

        for subset in itertools.permutations(grams_list,
                len(keyword.split())):
            # Prepare regex
            r = '.*?{0}.*'.format('.*'.join(subset))
            regex = re.compile(r, flags=re.I)

            for filename in files:
                with open(filename, 'r') as f:
                    data = f.read()
                    matches = regex.findall(data)
                    # Filter too long domains
                    if length:
                        matches = filter(check_lengh, matches)
                    domains.extend(matches)

        if not domains:
            return

        if sort and grams_length:
            domains = self.levsort(keyword, set(domains))

        get_str = lambda domain: re.sub('([.][a-z]{2,4})+$', '', domain)
        names = map(get_str, domains)

        domains = []
        for name in names:
            for zone in zone.split(','):
                domains.append('{0}.{1}'.format(name, zone))
        return domains

    def levsort(self, keyword, domains):
        """
        Sort domains by Levenshtein edit-distance

        :param sentence: str input source
        :param domains: domains list
        :rtype: list
        :return: sorted names list
        """
        # distance counter
        # transpositions - ab == ba
        distance = lambda s, d: edit_distance(s, d, transpositions=True)
        # remove zone
        get_str = lambda domain: re.sub('([.][a-z]{2,4})+$', '', domain)
        domains = map(get_str, domains)

        # Sorter
        for i in range(len(domains)):
            for j in range(len(domains) - 1):
                if (distance(keyword, get_str(domains[j])) >
                        distance(keyword, get_str(domains[j + 1]))):
                    tmp = copy(domains[j + 1])
                    domains[j + 1] = domains[j]
                    domains[j] = tmp

        return domains

if __name__ == '__main__':
    domainer = Domainer()
    domainer.cli_process()
