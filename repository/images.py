import mysql.connector

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="youdotcom_takehome_db",
        password="youdotcom_takehome_db",
        database="youdotcom_takehome_db",
    )

def upsert_image_metadata(image_index, title, url, file_path):
    """
    Insert or update metadata in image_metadata.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO image_metadata(image_index, title, url, file_path) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            title = VALUES(title),
            url = VALUES(url),
            file_path = VALUES(file_path),
            updated_at = CURRENT_TIMESTAMP
    """
    cursor.execute(query, (image_index, title, url, file_path))
    conn.commit()
    cursor.close()
    conn.close()


def get_image_metadata_by_index(image_index):
    """
    Fetch metadata by index from image_metadata.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM image_metadata WHERE image_index = %s"
    cursor.execute(query, (image_index,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_all_images_metadata():
    """
    Fetch all metadata from image_metadata.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM image_metadata"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
