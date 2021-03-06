import re
from collections import defaultdict

from billy.models import db
import logbook


logger = logbook.Logger('bathawk.actions')


class Actions(object):
    '''From this object, you can reference:
      * unmatched
      * matched
      * actions_list
    '''

    def __init__(self, abbr, patterns_module=None):
        self.abbr = abbr
        self.patterns_module = patterns_module
        self._build()

    def _build(self):

        if self.patterns_module:
            # Compile the patterns.
            patterns = self.patterns_module.patterns
            sub_patterns = self.patterns_module.sub_patterns

            # with open('%s.rgx.txt' % self.abbr) as f:
            #     patterns += filter(None, f.read().splitlines())
            patterns = [re.compile(p.format(**sub_patterns)) for p in patterns]
        else:
            patterns = []
        self.patterns = patterns

        # Get lists of un/matched actions.
        actions_list = filter(None, self._get_list())
        actions = set(actions_list)
        matched = set()
        unmatched = set(actions)
        for pattern in self.patterns:
            matched_pattern = set(filter(pattern.search, unmatched))
            matched |= matched_pattern
            unmatched -= matched

        self.unmatched = unmatched
        self.matched = matched
        self.list = actions_list

    def _get_list(self, only_other=True):
        '''Yield actions currently categorized as 'other'.
        '''
        meta = db.metadata.find_one(self.abbr)
        session = meta['terms'][-1]['sessions'][-1]
        msg = 'Retrieving actions for %r session %r'
        logger.info(msg % (self.abbr, session))
        action_ids = defaultdict(list)
        for bill in db.bills.find({'state': self.abbr, 'session': session},
                                  fields=['actions']):
            for action in bill['actions']:
                if only_other and action['type'] != ['other']:
                    continue
                action_text = action['action']
                action_ids[action_text].append(bill['_id'])
                yield action_text
        self.action_ids = action_ids

