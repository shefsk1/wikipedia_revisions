from datetime import datetime, timedelta
import itertools
from dateutil.relativedelta import relativedelta
import sqlite3
import json
from time import time
from path_util import old_database_path

def first_day_of_next_month(dt):
    '''Get the first day of the next month. Preserves the timezone.

    Args:
        dt (datetime.datetime): The current datetime

    Returns:
        datetime.datetime: The first day of the next month at 00:00:00.
    '''
    if dt.month == 12:
        return datetime(year=dt.year+1,
                                 month=1,
                                 day=1)
    else:
        return datetime(year=dt.year,
                                 month=dt.month+1,
                                 day=1)

def month_bin_revisions(rev_dict):
    ''' Bins the revisions into months '''
    bins = {}
    for page_name, revisions in rev_dict.items():
        # revisions = list(itertools.chain.from_iterable(rev_dict.values()))
        revisions.sort(key= lambda x: datetime.fromisoformat(x["timestamp"]))




        earliest_page_conception = datetime.fromisoformat(revisions[0]["timestamp"])

        bin_start = earliest_page_conception.replace(day=1,hour=0,minute=0,second=0,microsecond=0)

        bins[page_name] = { bin_start : []}
        bin_end = first_day_of_next_month(bin_start)

        for revision in revisions:
            
            if "mw-reverted" in revision["tags"]:
                continue
            

            time_of_revision = datetime.fromisoformat(revision["timestamp"])
            if time_of_revision < bin_end:
                bins[page_name][bin_start].append(revision)
            else:
                bin_start = time_of_revision.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
                bin_end = first_day_of_next_month(bin_start)
                bins[page_name][bin_start] = [revision]

    return bins


db_path = old_database_path
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("SELECT lenient_revisions FROM occupations")
occupations =  cur.fetchall()
all_revs = []
for occ in occupations:
    revision_dict = month_bin_revisions(json.loads(occ[0]))
    all_revs.append(revision_dict)

print(all_revs[0])  # TODO remove
