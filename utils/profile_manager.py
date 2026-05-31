from utils.database import get_db, UserProfileModel
import logging

def load_profile() -> dict:
    """
    Loads the global student persona profile from the SQL database.
    """
    db = get_db()
    try:
        profile = db.query(UserProfileModel).order_by(UserProfileModel.id.desc()).first()
        if profile:
            return {
                "education_level": profile.education_level,
                "interests": profile.interests
            }
    except Exception as e:
        logging.error(f"Error loading profile from database: {e}")
    finally:
        db.close()
    return {}

def save_profile(profile_dict: dict):
    """
    Saves the global student persona profile in the SQL database.
    """
    db = get_db()
    try:
        # Get existing or create new
        profile = db.query(UserProfileModel).order_by(UserProfileModel.id.desc()).first()
        if not profile:
            profile = UserProfileModel()
            db.add(profile)
        
        profile.education_level = profile_dict.get("education_level", "College Undergraduate")
        profile.interests = profile_dict.get("interests", "General")
        
        db.commit()
    except Exception as e:
        logging.error(f"Error saving profile to database: {e}")
        db.rollback()
    finally:
        db.close()

