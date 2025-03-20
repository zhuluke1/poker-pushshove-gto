# api/app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add root directory to sys.path

from flask import Flask, render_template, request
import pandas as pd
from gto_calculator import calculate_push_fold_gto  # Now this should work

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default values
    stack_size = 10.0
    position = "sb"
    error = None
    sb_table = None
    bb_table = None

    if request.method == 'POST':
        try:
            stack_size = float(request.form.get('stack_size', 10.0))
            position = request.form.get('position', 'sb')

            # Calculate GTO ranges
            sb_pos = position == "sb"
            sb_strategy, bb_strategy = calculate_push_fold_gto(stack_size)

            # Prepare DataFrames
            df_sb = pd.DataFrame.from_dict(sb_strategy, orient='index', columns=['Push Frequency'])
            df_sb = df_sb.sort_values(by='Push Frequency', ascending=False)
            df_bb = pd.DataFrame.from_dict(bb_strategy, orient='index', columns=['Call Frequency'])
            df_bb = df_bb.sort_values(by='Call Frequency', ascending=False)

            # Convert DataFrames to HTML tables (top 20 hands)
            sb_table = df_sb.head(20).to_html(classes='table table-striped', index=True)
            bb_table = df_bb.head(20).to_html(classes='table table-striped', index=True)

        except Exception as e:
            error = f"Error calculating GTO ranges: {str(e)}"

    return render_template('index.html', stack_size=stack_size, position=position,
                         sb_table=sb_table, bb_table=bb_table, error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)