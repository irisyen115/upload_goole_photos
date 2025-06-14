from flask import Blueprint, request, jsonify
from lib.google import (
    get_service,
    get_albums_with_cover_urls,
    authenticate
)
import logging
import requests
from config.config import Config

logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

album_db = Blueprint('album_db', __name__)
@album_db.route('/list_albums', methods=['POST'])
def get_albums():
    """取得 Google Photos 相簿列表"""
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400
    creds = authenticate()
    if not creds:
        return jsonify({"error": "Credentials are required"}), 400

    service = get_service(creds)
    if not service:
        return jsonify({"error": "Failed to create Google Photos service"}), 500

    try:
        albums = get_albums_with_cover_urls(service)
        if not albums:
            return jsonify({"message": "No albums found"}), 404
        logging.error(f"Fetched albums: {albums}")
        album_titles = [album['title'] for album in albums if 'title' in album]
        cover_url = [album['cover_url'] for album in albums if 'cover_url' in album]
        logging.error(f"Album titles: {album_titles}, Cover URLs: {cover_url}")
        if not album_titles:
            return jsonify({"message": "No album titles found"}), 404
        requests.post(f"{Config.SERVER_URL}/api/line/album", json={
            "album_titles": album_titles,
            "covers": cover_url,
            "token": token
        })
        logging.error(f"Albums fetched: {album_titles}")
        return jsonify(album_titles), 200
    except Exception as e:
        logging.error(f"Error fetching albums: {e}")
        return jsonify({"error": str(e)}), 500