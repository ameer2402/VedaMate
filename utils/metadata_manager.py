import json
import logging
from utils.database import get_db, TextbookMetadataModel

def load_metadata(pdf_name: str) -> dict:
    """
    Loads textbook-specific metadata from the database.
    """
    db = get_db()
    try:
        record = db.query(TextbookMetadataModel).filter(TextbookMetadataModel.pdf_name == pdf_name).first()
        if record and record.metadata_json:
            return json.loads(record.metadata_json)
    except Exception as e:
        logging.error(f"Error loading metadata for {pdf_name} from database: {e}")
    finally:
        db.close()
    return {"persona": {}, "syllabus": [], "chat_history": {}}

def save_metadata(pdf_name: str, data: dict):
    """
    Saves/Updates textbook-specific metadata in the database.
    """
    db = get_db()
    try:
        record = db.query(TextbookMetadataModel).filter(TextbookMetadataModel.pdf_name == pdf_name).first()
        if not record:
            record = TextbookMetadataModel(pdf_name=pdf_name)
            db.add(record)
        
        record.metadata_json = json.dumps(data)
        db.commit()
    except Exception as e:
        logging.error(f"Error saving metadata for {pdf_name} to database: {e}")
        db.rollback()
    finally:
        db.close()

