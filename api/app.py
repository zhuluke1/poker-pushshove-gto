# api/app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, Response
from flask_caching import Cache
import pandas as pd
from gto_calculator import calculate_push_fold_gto

app = Flask(__name__)

cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 3600
}
app.config.from_mapping(cache_config)
cache = Cache(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    stack_size = 10.0
    position = "sb"
    error = None
    sb_strategy = None
    bb_strategy = None
    sb_push_ev = None
    bb_call_ev = None

    if request.method == 'POST':
        try:
            # Validate stack size
            stack_size_input = request.form.get('stack_size', '10.0')
            stack_size = float(stack_size_input)
            if stack_size < 1 or stack_size > 100:
                raise ValueError("Stack size must be between 1 and 100 big blinds.")

            position = request.form.get('position', 'sb')
            if position not in ['sb', 'bb']:
                raise ValueError("Position must be 'sb' or 'bb'.")

            # Calculate GTO ranges (cached)
            sb_pos = position == "sb"
            sb_strategy, bb_strategy, sb_push_ev, bb_call_ev = get_cached_gto(stack_size)

        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Error calculating GTO ranges: {str(e)}"

    return render_template('index.html', stack_size=stack_size, position=position,
                         sb_strategy=sb_strategy, bb_strategy=bb_strategy,
                         sb_push_ev=sb_push_ev, bb_call_ev=bb_call_ev, error=error)

@cache.memoize(timeout=3600)
def get_cached_gto(stack_size):
    return calculate_push_fold_gto(stack_size, sb_pos=True)

@app.route('/download/<strategy>/<float:stack_size>')
def download(strategy, stack_size):
    if stack_size < 1 or stack_size > 100:
        return "Stack size must be between 1 and 100 big blinds.", 400

    sb_strategy, bb_strategy, sb_push_ev, bb_call_ev = get_cached_gto(stack_size)
    
    if strategy == 'sb':
        df = pd.DataFrame({
            'Push Frequency': sb_strategy,
            'Push EV': sb_push_ev
        })
        filename = f"sb_push_strategy_{stack_size}bb.csv"
    else:
        df = pd.DataFrame({
            'Call Frequency': bb_strategy,
            'Call EV': bb_call_ev
        })
        filename = f"bb_call_strategy_{stack_size}bb.csv"
    
    df = df.sort_values(by=df.columns[0], ascending=False)
    csv = df.to_csv()
    
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)