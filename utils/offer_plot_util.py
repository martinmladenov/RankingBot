from datetime import date, datetime
from matplotlib import pyplot as plt, dates as mdates
from utils import programmes_util

filename = 'offers.png'


async def generate_graph(programme: programmes_util.Programme, db_conn):
    rows = await db_conn.fetch(
        'SELECT m.rank, ud.is_private, m.offer_date FROM '
        '(SELECT MAX(rank) as rank, offer_date, programme FROM ranks '
        'WHERE programme = $1 AND rank > $2 AND offer_date IS NOT NULL '
        'GROUP BY offer_date, programme) AS m '
        'JOIN ranks r ON m.rank = r.rank AND m.offer_date = r.offer_date AND m.programme = r.programme '
        'LEFT JOIN user_data ud on r.user_id = ud.user_id '
        'ORDER BY m.offer_date', programme.id, programme.places)

    x_values = [date(2020, 4, 15)]
    y_values = [programme.places]

    if rows:
        for i in range(len(rows)):
            row = rows[i]
            rank = row[0]
            is_private = row[1]
            offer_date = row[2]

            # Round rank if it's private
            if is_private:
                rank = round_rank(rank)

                # make sure it's not lower than the previous rank
                if i > 0 and rank < y_values[i - 1]:
                    rank = y_values[i - 1]

                # make sure it's not higher than the next public rank
                for j in range(i, len(rows)):
                    if not rows[j][1]:
                        if rank > rows[j][0]:
                            rank = rows[j][0]
                        break

            x_values.append(offer_date)
            y_values.append(rank)

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
