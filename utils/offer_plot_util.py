from datetime import date, datetime
from matplotlib import pyplot as plt, dates as mdates, RcParams
from utils import programmes_util
from database import db_fetchall

filename = 'offers.png'


def generate_graph(programme: programmes_util.Programme):
    rows = db_fetchall('SELECT rank, is_private, offer_date FROM ranks '
                       'LEFT JOIN user_data ON ranks.user_id = user_data.user_id '
                       'WHERE programme = %s AND rank > %s AND offer_date IS NOT NULL '
                       'AND (is_private IS NULL OR is_private = FALSE) '
                       'ORDER BY offer_date, rank', (programme.id, programme.places))

    x_values = [date(2020, 4, 15)]
    y_values = [programme.places]

    if rows:
        for row in rows:
            x_values.append(row[2])
            y_values.append(row[0])

        x_values.append(datetime.utcnow().date())
        y_values.append(rows[len(rows) - 1][0])

    fill_between_end = programme.places - (y_values[len(y_values) - 1] - programme.places) / 15
    bottom_limit = fill_between_end - (y_values[len(y_values) - 1] - fill_between_end) / 40

    bg_color = '#36393F'

    plt.rcParams['ytick.color'] = 'w'
    plt.rcParams['xtick.color'] = 'w'
    plt.rcParams['axes.edgecolor'] = 'w'
    plt.rcParams['axes.labelcolor'] = '#767676'

    ax = plt.gca()
    formatter = mdates.DateFormatter("%d %b")
    ax.xaxis.set_major_formatter(formatter)
    locator = mdates.WeekdayLocator(byweekday=mdates.WEDNESDAY)
    ax.xaxis.set_major_locator(locator)
    ax.set_xlabel('Offer date')
    ax.set_ylabel('Ranking number')

    plt.setp(ax.spines.values(), visible=False)
    ax.set_facecolor(bg_color)

    ax.set_axisbelow(True)
    plt.grid(color='#444444', linestyle='--')

    plt.step(x_values, y_values, where='post')
    plt.fill_between(x_values, y_values, y2=fill_between_end, step="post", alpha=0.35)
    plt.title(f'{programme.uni_name} {programme.display_name}', color='w')
    ax.set_ylim(bottom=bottom_limit)

    plt.savefig(filename, facecolor=bg_color)
    plt.close()


def round_rank(number, base=5):
    return base * round(number / base)
