import logging
from datetime import datetime

from django.db.models import Q

from news_crawler.models import RedditUser, Submision

logger = logging.getLogger(__name__)

__all__ = ['process_submission', 'get_submision_title', 'get_submision_submitter',
           'get_submision_url', 'get_submision_creation_date', 'get_submision_creation_date',
           'get_submision_punctuation', 'get_submision_punctuation', 'get_submision_rank',
           'get_submisions_comments', 'get_comments_url', 'get_submitter_url']

def process_submission(submision):
    '''
    Function that from a python subreddit submision extract:
        - submisions title
        - externals url
        - discusion url
        - submitter
        - punctuation
        - creation_date
        - number_of_comments
        - comments
        - users
    and save them into db
    '''
    sub = {}
    submission = None
    sub['title'] = get_submision_title(submision)

    if 'self' not in submision.get('class'):
        sub['external_url'] = get_submision_url(submision)
    else:
        sub['discusion_url'] = get_submision_url(submision)

    sub['submitter'] = get_submision_submitter(submision)
    sub['punctuation'] = get_submision_punctuation(submision)
    sub['rank'] = get_submision_rank(submision)
    sub['creation_date'] = get_submision_creation_date(submision)
    sub['number_of_comments'] = get_submisions_comments(submision)
    sub['comments_url'] = get_comments_url(submision)
    sub['submitter_url'] = get_submitter_url(submision)

    qsub = Q(submitter=sub['submitter'], title=sub['title'])
    try:
        submisions = Submision.objects.filter(qsub)
        if submisions.exists():
            submisions.update(**sub)
            submision = submisions.first()
        else:
            submission = Submision.objects.create(**sub)
    except Exception as e:
        logger.exception(e)

    return submision


def get_submision_title(submision):
    title_fields = submision.cssselect('a[class^="title"]')
    return title_fields[0].text if title_fields else ''


def get_submision_url(submision):
    return submision.get('data-url')


def get_submision_submitter(submision):
    author = submision.get('data-author')
    return RedditUser.objects.get_or_create(name=author)[0]


def get_submision_creation_date(submision):
    time_stamp = submision.get('data-timestamp')
    return datetime.utcfromtimestamp(int(time_stamp)/1000)


def get_submision_punctuation(submision):
    punctuation_elem = submision.cssselect('[class="score unvoted"]')
    if punctuation_elem and punctuation_elem[0].text != u'•':
        return int(punctuation_elem[0].text)

    return 0


def get_submision_rank(submision):
    rank = submision.get('data-rank')
    return int(rank) if rank else 0


def get_submisions_comments(submision):
    comments = submision.cssselect('li > a[class~="comments"]')
    if comments:
        if len(comments[0].text.split(' ')) == 2:
            return int(comments[0].text.split(' ')[0])
    return 0


def get_comments_url(submision):
    comments_elem = submision.cssselect('li > a[class~="comments"]')
    return comments_elem[0].get('href') if comments_elem  else ''


def get_submitter_url(submison):
    submitter_url_elem = submison.cssselect('p > a[class~="author"]')
    return submitter_url_elem[0].get('href') if submitter_url_elem else ''