from flask import Blueprint, jsonify
from flaskr import db
from datetime import datetime

bp = Blueprint('stats', __name__, url_prefix='/api')

@bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        
        # Total counts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM image
            GROUP BY status
        """)
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        processing_count = status_counts.get('processing', 0)
        processed_count = status_counts.get('processed', 0)
        
        # Average processing time in seconds (processed only)
        cursor.execute("""
            SELECT AVG(
                strftime('%s', processed_at) - strftime('%s', created_at)
            ) as avg_time
            FROM image
            WHERE status = 'processed'
        """)
        row = cursor.fetchone()
        avg_processing_time = row['avg_time'] if row and row['avg_time'] is not None else 0
        
        return jsonify({
            "processing_count": processing_count,
            "processed_count": processed_count,
            "average_processing_time_seconds": avg_processing_time
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch statistics",
            "details": str(e)
        }), 500