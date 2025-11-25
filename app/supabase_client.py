import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "SSIS")

def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_student_photo(file_data: bytes, student_id: str, file_extension: str = "jpg") -> str:
    """
    Upload a student photo to Supabase storage.
    
    Args:
        file_data: Binary file data
        student_id: Student ID (used as filename)
        file_extension: File extension (default: jpg)
    
    Returns:
        Public URL of the uploaded file
    """
    try:
        supabase = get_supabase_client()
        
        # Create filename: student_id.extension
        filename = f"{student_id}.{file_extension}"
        file_path = f"students/{filename}"
        
        # Upload file to Supabase storage
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            file_path,
            file_data,
            file_options={"content-type": f"image/{file_extension}", "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        
        return public_url
    except Exception as e:
        raise Exception(f"Failed to upload photo to Supabase: {str(e)}")

def delete_student_photo(photo_url: str) -> bool:
    """
    Delete a student photo from Supabase storage.
    
    Args:
        photo_url: Public URL of the photo
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not photo_url:
            return True
        
        supabase = get_supabase_client()
        
        # Extract file path from URL
        # URL format: https://[project].supabase.co/storage/v1/object/public/[bucket]/[path]
        if "/storage/v1/object/public/" in photo_url:
            path_part = photo_url.split("/storage/v1/object/public/")[1]
            # Remove bucket name from path
            if path_part.startswith(f"{SUPABASE_BUCKET}/"):
                file_path = path_part[len(f"{SUPABASE_BUCKET}/"):]
            else:
                file_path = path_part.split("/", 1)[1] if "/" in path_part else path_part
        else:
            # Fallback: try to extract from URL
            return False
        
        # Delete file
        supabase.storage.from_(SUPABASE_BUCKET).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting photo: {str(e)}")
        return False

