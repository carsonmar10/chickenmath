from flask import Flask, request, render_template
# Import the initialize_database function
import sqlite3
from init_db import initialize_database

app = Flask(__name__)

def calculate_fertilized_eggs(num_roosters, num_hens, fertilization_rate, max_hens_per_rooster=10):
    effectively_fertilized_hens = min(num_hens, num_roosters * max_hens_per_rooster)
    fertilized_eggs_per_day = round(effectively_fertilized_hens * (5 / 7) * fertilization_rate)
    fertilized_eggs_per_week = round(fertilized_eggs_per_day * 7)
    fertilized_eggs_per_month = round(fertilized_eggs_per_day * 30)  # Approximation
    fertilized_eggs_per_year = round(fertilized_eggs_per_day * 365)

    return fertilized_eggs_per_day, fertilized_eggs_per_week, fertilized_eggs_per_month, fertilized_eggs_per_year


def calculate_hatched_eggs(fertilized_eggs_per_year, incubator_capacity, hatch_rate, incubation_period=21):
    # Total batches of eggs that can be incubated in a year
    total_batches_per_year = 365 // incubation_period

    eggs_per_batch = min(incubator_capacity, fertilized_eggs_per_year // total_batches_per_year)

    hatched_eggs_per_year = round(eggs_per_batch * hatch_rate * total_batches_per_year)
    hatched_eggs_per_month = round(hatched_eggs_per_year / 12)
    hatched_eggs_per_week = round(hatched_eggs_per_year / 52)
    hatched_eggs_per_day = round(hatched_eggs_per_year / 365)

    return hatched_eggs_per_day, hatched_eggs_per_week, hatched_eggs_per_month, hatched_eggs_per_year

def calculate_feed_requirements(num_hens, num_roosters):
    daily_feed_consumption_per_chicken = 0.25  # pounds
    total_chickens = num_hens + num_roosters

    daily_feed = total_chickens * daily_feed_consumption_per_chicken
    weekly_feed = daily_feed * 7
    monthly_feed = daily_feed * 30  # Approximation
    yearly_feed = daily_feed * 365

    return daily_feed, weekly_feed, monthly_feed, yearly_feed

def calculate_space_requirements(num_hens, num_roosters):
    space_per_chicken_coop = 4  # square feet
    space_per_chicken_run = 8  # square feet
    total_chickens = num_hens + num_roosters

    coop_space = total_chickens * space_per_chicken_coop
    run_space = total_chickens * space_per_chicken_run

    return coop_space, run_space

def perform_calculations(num_hens, num_roosters=None, incubator_capacity=None):
    try:
        num_hens = int(num_hens)
        num_roosters = int(num_roosters) if num_roosters is not None else 0
        incubator_capacity = int(incubator_capacity) if incubator_capacity is not None else 0
    except ValueError:
        return "Input Invalid"

    with sqlite3.connect('chickenmath.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT eggs_per_week, fertilization_rate, hatch_rate FROM farm_data WHERE id=1")
        data = cursor.fetchone()

    if data:
        eggs_per_week, fertilization_rate, hatch_rate = data

        total_eggs_per_day = round((num_hens * eggs_per_week) / 7)
        total_eggs_per_week = round(num_hens * eggs_per_week)
        total_eggs_per_month = round(num_hens * eggs_per_week * 52 / 12)
        total_eggs_per_year = round(num_hens * eggs_per_week * 52)

        if num_roosters > 0:
            fertilized_eggs_per_day, fertilized_eggs_per_week, fertilized_eggs_per_month, fertilized_eggs_per_year = calculate_fertilized_eggs(num_roosters, num_hens, fertilization_rate)
        else:
            fertilized_eggs_per_day = fertilized_eggs_per_week = fertilized_eggs_per_month = fertilized_eggs_per_year = 0

        if incubator_capacity > 0 and num_roosters > 0:
            hatched_eggs_per_day, hatched_eggs_per_week, hatched_eggs_per_month, hatched_eggs_per_year = calculate_hatched_eggs(fertilized_eggs_per_year, incubator_capacity, hatch_rate)
        else:
            hatched_eggs_per_day = hatched_eggs_per_week = hatched_eggs_per_month = hatched_eggs_per_year = 0

        daily_feed, weekly_feed, monthly_feed, yearly_feed = calculate_feed_requirements(num_hens, num_roosters)
        coop_space, run_space = calculate_space_requirements(num_hens, num_roosters)

        calculated_result = {
            'total_eggs_per_day': total_eggs_per_day,
            'total_eggs_per_week': total_eggs_per_week,
            'total_eggs_per_month': total_eggs_per_month,
            'total_eggs_per_year': total_eggs_per_year,
            'fertilized_eggs_per_day': fertilized_eggs_per_day,
            'fertilized_eggs_per_week': fertilized_eggs_per_week,
            'fertilized_eggs_per_month': fertilized_eggs_per_month,
            'fertilized_eggs_per_year': fertilized_eggs_per_year,
            'hatched_eggs_per_day': hatched_eggs_per_day,
            'hatched_eggs_per_week': hatched_eggs_per_week,
            'hatched_eggs_per_month': hatched_eggs_per_month,
            'hatched_eggs_per_year': hatched_eggs_per_year,
            'daily_feed': daily_feed,
            'weekly_feed': weekly_feed,
            'monthly_feed': monthly_feed,
            'yearly_feed': yearly_feed,
            'coop_space': coop_space,
            'run_space': run_space
        }

        return calculated_result
    else:
        return "No data available for calculations."

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_hens = request.form.get('num_hens')
        num_roosters = request.form.get('num_roosters') or None
        incubator_capacity = request.form.get('incubator_capacity') or None
        result = perform_calculations(num_hens, num_roosters, incubator_capacity)
        return render_template('index.html', result=result, num_hens=num_hens, num_roosters=num_roosters, incubator_capacity=incubator_capacity)
    return render_template('index.html')

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
