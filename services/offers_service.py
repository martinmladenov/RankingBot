from datetime import date, datetime, timedelta
from matplotlib import pyplot as plt, dates as mdates
from matplotlib.ticker import MaxNLocator
from helpers import programmes_helper
import uuid
import os

filename_format = '3TU_Discord_offers_%s.png'


class OffersService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def generate_uuid(self) -> str:
        # Generate a version 1 UUID containing the current date and time
        return str(uuid.uuid1(node=1))

    async def clean_up_file(self, filename: str):
        os.remove(filename)

    async def generate_graph(self, programme: programmes_helper.Programme, step: bool, year: int) -> str:
        if year not in programme.places:
            raise ValueError

        rows = await self.db_conn.fetch(
            'SELECT rank, is_private, offer_date FROM ranks '
            'WHERE programme = $1 AND rank > $2 AND offer_date IS NOT NULL AND year = $3 '
            'ORDER BY offer_date, rank', programme.id, programme.places[year], year)

        x_values = [date(year, 4, 15)]
        y_values = [programme.places[year]]

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

            end_date = date(year, 8, 15)
            curr_date = datetime.utcnow().date()
            x_values.append(min(end_date, curr_date))
            y_values.append(y_values[len(y_values) - 1])

        fill_between_end = programme.places[year] - (y_values[len(y_values) - 1] - programme.places[year]) / 15
        bottom_limit = fill_between_end - (y_values[len(y_values) - 1] - fill_between_end) / 40

        bg_color = '#36393F'
        fg_color = programme.graph_colour

        plt.rcParams['ytick.color'] = 'w'
        plt.rcParams['xtick.color'] = 'w'
        plt.rcParams['axes.edgecolor'] = 'w'
        plt.rcParams['axes.labelcolor'] = '#767676'

        ax = plt.gca()
        formatter = mdates.DateFormatter("%d %b")
        ax.xaxis.set_major_formatter(formatter)
        locator = mdates.WeekdayLocator(byweekday=x_values[0].weekday())
        ax.xaxis.set_major_locator(locator)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel('Offer date')
        ax.set_ylabel('Ranking number')

        plt.setp(ax.spines.values(), visible=False)
        ax.set_facecolor(bg_color)

        ax.set_axisbelow(True)
        plt.grid(color='#444444', linestyle='--')

        if programme.visa_cutoff is not None:
            cutoff_date = date(year, programme.visa_cutoff[1], programme.visa_cutoff[0])
            if (datetime.utcnow() + timedelta(days=20)).date() >= cutoff_date:
                plt.axvline(cutoff_date, ymin=0.02, linestyle='--', alpha=0.7, color=fg_color)
                plt.text(cutoff_date, y_values[-1], "Non-EU cutoff", rotation='vertical', color=fg_color,
                         verticalalignment='center_baseline', horizontalalignment='right', stretch='condensed',
                         fontsize='small', fontweight='ultralight', fontstyle='italic')

        if not step:
            plt.plot(x_values, y_values, linestyle='--', color=fg_color)
            plt.fill_between(x_values, y_values, y2=fill_between_end, alpha=0.15, color=fg_color)

        plt.step(x_values, y_values, where='post', alpha=(0.5 if not step else None), color=fg_color)
        plt.fill_between(x_values, y_values, y2=fill_between_end, step="post", alpha=(0.20 if not step else 0.35),
                         color=fg_color)
        plt.title(f'{programme.uni_name} {programme.display_name} ({year})', color='w')
        ax.set_ylim(bottom=bottom_limit)

        # only show every second week
        for label in ax.get_xaxis().get_ticklabels()[1::2]:
            label.set_visible(False)
        for label in ax.get_xaxis().get_major_ticks()[1::2]:
            label.set_visible(False)

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        filename = filename_format % await self.generate_uuid()

        plt.savefig(filename, facecolor=bg_color, dpi=200)
        plt.close()

        return filename

    async def get_highest_ranks_with_offers(self, year):
        offers = await self.db_conn.fetch(
            'select r.programme, r.rank, MAX(d.offer_date), d.is_private '
            'from (select programme, max(rank) as rank from ranks '
            'where ranks.offer_date is not null and ranks.year = $1 '
            'group by programme) as r '
            'inner join ranks as d '
            'on r.programme = d.programme and r.rank = d.rank and d.year = $1 '
            'and d.offer_date is not null '
            'group by r.programme, r.rank, d.is_private '
            'order by MAX(d.offer_date) desc', year)

        for i in range(len(offers)):
            programme_id, rank = offers[i][0:2]
            places = programmes_helper.programmes[programme_id].places[year]
            if rank <= places:
                offers[i] = (programme_id, places, date(year, 4, 15), False)

        return offers


def round_rank(number, base=5):
    return base * round(number / base)
