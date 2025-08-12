import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from scraper import CompetitorScraper
import json
from datetime import datetime, timezone
import dateutil.parser

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize the scraper
scraper = CompetitorScraper()

# Custom template filters
@app.template_filter('from_iso')
def from_iso_filter(date_string):
    """Convert ISO date string to datetime object"""
    if not date_string:
        return datetime.now()
    try:
        return dateutil.parser.parse(date_string)
    except:
        return datetime.now()

@app.template_filter('timesince')
def timesince_filter(dt):
    """Calculate time since given datetime"""
    if not dt:
        return "unknown"
    
    if isinstance(dt, str):
        try:
            dt = dateutil.parser.parse(dt)
        except:
            return "unknown"
    
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return "just now"

@app.route('/')
def index():
    """Main dashboard showing competitor pricing data"""
    try:
        data = scraper.get_all_data()
        return render_template('index.html', data=data)
    except Exception as e:
        logging.error(f"Error loading dashboard: {str(e)}")
        flash(f"Error loading data: {str(e)}", "error")
        return render_template('index.html', data={})

@app.route('/refresh', methods=['POST'])
def refresh_data():
    """Manually trigger a refresh of all competitor data"""
    try:
        logging.info("Starting manual refresh of competitor data")
        results = scraper.scrape_all()
        
        success_count = sum(1 for result in results.values() if result.get('success'))
        total_count = len(results)
        
        if success_count == total_count:
            flash(f"Successfully updated all {success_count} competitors", "success")
        elif success_count > 0:
            flash(f"Updated {success_count} out of {total_count} competitors. Check logs for errors.", "warning")
        else:
            flash("Failed to update any competitor data. Check logs for errors.", "error")
            
        logging.info(f"Refresh completed: {success_count}/{total_count} successful")
        
    except Exception as e:
        logging.error(f"Error during refresh: {str(e)}")
        flash(f"Error during refresh: {str(e)}", "error")
    
    return redirect(url_for('index'))

@app.route('/refresh/<competitor>')
def refresh_single(competitor):
    """Refresh data for a single competitor"""
    try:
        result = scraper.scrape_single(competitor)
        if result.get('success'):
            flash(f"Successfully updated {competitor}", "success")
        else:
            flash(f"Failed to update {competitor}: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        logging.error(f"Error refreshing {competitor}: {str(e)}")
        flash(f"Error refreshing {competitor}: {str(e)}", "error")
    
    return redirect(url_for('index'))

@app.route('/export')
def export_data():
    """Export all competitor data as JSON"""
    try:
        data = scraper.get_all_data()
        return jsonify(data), 200, {
            'Content-Type': 'application/json',
            'Content-Disposition': f'attachment; filename=competitor_pricing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        }
    except Exception as e:
        logging.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data')
def api_data():
    """API endpoint to get all data"""
    try:
        data = scraper.get_all_data()
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error getting API data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', data={}), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    flash("An internal server error occurred", "error")
    return render_template('index.html', data={}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
